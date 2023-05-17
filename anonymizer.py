#!/usr/bin/env python3

import collections
import csv
import io
import os.path
import random
import re
import sys
import zipfile
from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from pathlib import Path
from typing import (
    ClassVar,
    Iterable,
    Iterator,
    Optional,
    Type,
    Union,
)

from gooey import (
    Gooey,
    GooeyParser,
)

ENCODED_DIGITS = 16
ENC_PATTERN = re.compile(r"enc-\d{16}")  # make sure this matches ENCODED_DIGITS
REPORT_PROGRESS = True


def random_digits():
    return ''.join(str(random.randint(0, 9)) for _ in range(ENCODED_DIGITS))


class ZipPath(zipfile.Path):
    @property
    def stem(self) -> str:
        return Path(str(self)).stem

    @property
    def suffix(self) -> str:
        return Path(str(self)).suffix

    def iterdir(self) -> Iterator['ZipPath']:  # noqa (iterdir is not a word)
        for entry in super().iterdir():
            yield ZipPath.from_zip_path(entry)

    @classmethod
    def from_zip_path(cls, entry: zipfile.Path) -> 'ZipPath':
        return cls(
            entry.root.filename,  # noqa (root.filename is like a private interface)
            at=entry.at,  # noqa (at is like a private interface)
        )


FilePath = Union[Path, ZipPath]


class QueueItem(ABC):
    def __init__(self, path: FilePath):
        self.path: FilePath = path

    @abstractmethod
    def process(self, worker: 'Worker'):
        raise NotImplementedError()

    def output_name(self) -> str:
        return self.path.name

    def __str__(self) -> str:
        return f'{self.path}'


class EncodeItem(QueueItem, ABC):
    def __init__(self, path: FilePath, config: 'BaseConfig'):
        super().__init__(path)
        self.config = config

    def process(self, worker: 'Worker'):
        dest = io.StringIO()
        self.config.map_file(self.path, worker, dest)
        worker.output_zipfile.writestr(worker.unique_output_name(self.output_name()), dest.getvalue())


class DecodeItem(QueueItem, ABC):
    def process(self, worker: 'Worker'):
        with self.path.open() as source:
            content = source.read()
            content = ENC_PATTERN.sub(worker.encoded_replace, content)
        worker.output_zipfile.writestr(worker.unique_output_name(self.output_name()), content)


class Worker:
    def __init__(self, output_directory: str, output_zipname: Optional[str] = None, should_save_mappings: bool = True):
        self.output_directory: Path = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)

        self.encoded_mappings: dict[str, str] = {}
        self.encoded_values: set[str] = set()
        self.input_zipfiles: dict[Path, zipfile.ZipFile] = {}
        self.filesizes: list[int] = []
        self.queue: list[QueueItem] = []
        self.output_names: set[str] = set()
        output_zipname = output_zipname or 'output.zip'  # TODO: timestamped name by default?
        self.output_zipfile: zipfile.ZipFile = \
            zipfile.ZipFile(self.output_directory / output_zipname, mode="w", compression=zipfile.ZIP_DEFLATED)
        self.should_save_mappings = should_save_mappings
        self.processed_count: int = 0

    def unique_output_name(self, name: str):
        if name in self.output_names:
            suffix = 2
            while f'{name}.{suffix}' in self.output_names:
                suffix += 1
            name = f'{name}.{suffix}'
        self.output_names.add(name)
        return name

    def encoded_replace(self, match: re.Match):
        return self.encoded_mappings[match.group()]

    def _list_files(self, paths: Iterable[str]) -> list[FilePath]:
        """
        Lists all files inside all provided paths, including inside of zip archives.

        We'll be using this later on to search for files in the same directories with e.g. header order list.
        """
        paths: collections.deque[FilePath] = collections.deque(Path(x) for x in paths)
        all_files = []
        while paths:
            path = paths.popleft()
            if not path.exists():
                print(f'{path} does not exist, skipping')
                continue

            if path.is_dir():
                paths.extend(path.iterdir())
                continue

            if path.suffix.lower().endswith('.zip'):
                paths.extend(ZipPath(path, '').iterdir())
                continue

            all_files.append(path)
        return all_files

    def find_files(self, paths: list, for_encode: bool) -> None:
        list_of_files = self._list_files(paths)
        print(f'Listed {len(list_of_files)} files.')
        for file_path in list_of_files:
            if for_encode:
                config = ConfigFactory.get_config(file_path.name)
                if config is None:
                    continue
                self.queue.append(EncodeItem(file_path, config))
            else:
                self.queue.append(DecodeItem(file_path))

            self.filesizes.append(file_path.stat().st_size)

    def encode_value(self, value: str) -> str:
        if not value:
            return ''
        try:
            return self.encoded_mappings[value]
        except KeyError:
            while True:
                encoded = 'enc-' + random_digits()
                if encoded not in self.encoded_values:
                    self.encoded_values.add(encoded)
                    break
            self.encoded_mappings[value] = encoded
            return encoded

    def process_files(self):
        total = len(self.queue)
        total_file_size = sum(self.filesizes)
        processed_bytes = 0
        for queue_item, filesize in zip(self.queue, self.filesizes):
            self.processed_count += 1
            print(f'Processing file {queue_item} ({self.processed_count}/{total})')
            queue_item.process(self)
            processed_bytes += filesize
            if REPORT_PROGRESS:
                print(f'Progress {int((processed_bytes * 100) / total_file_size)}%')
        print(f'Successfully processed {self.processed_count} data files')

    def save_mappings(self):
        # TODO: write to temp and rename?
        with open(self.output_directory / 'mapping.tsv', mode="w", encoding='utf-8') as f:
            writer = csv.writer(f, dialect='excel-tab')
            writer.writerows(sorted(self.encoded_mappings.items()))

    def load_mappings(self, path):
        with open(path, mode="r", encoding='utf-8') as f:
            reader = csv.reader(f, dialect='excel-tab')
            self.encoded_mappings = dict((x[1].strip(), x[0].strip()) for x in reader if len(x) == 2)
            self.encoded_values = set(self.encoded_mappings.values())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.output_zipfile.close()
        for f in self.input_zipfiles.values():
            f.close()
        if self.should_save_mappings:
            self.save_mappings()


@dataclass
class BaseConfig:
    CONFIG_TYPE: ClassVar[str] = None

    file_mask: str

    def matches(self, filename: str) -> bool:
        return re.match(self.file_mask, filename) is not None

    @abstractmethod
    def map_file(self, in_file: FilePath, worker: Worker, destination: io.TextIOBase) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_description(self) -> dict[str, str]:
        raise NotImplementedError

    def make_description(self, title: str, caption: str, message: str) -> dict[str, str]:
        return {
            'type': 'MessageDialog',
            'menuTitle': title,
            'caption': caption,
            'message': message,
        }


class ConfigFactory:
    REGISTERED: ClassVar[dict[str, Type[BaseConfig]]] = []
    LOADED: ClassVar[list[BaseConfig]] = []

    @classmethod
    def register(cls, config_class: Type[BaseConfig]) -> None:
        cls.REGISTERED[config_class.CONFIG_TYPE] = config_class

    @classmethod
    def get_config(cls, filename: str) -> Optional[BaseConfig]:
        return next((config for config in cls.LOADED if config.matches(filename)), None)

    @classmethod
    def get_config_descriptions(cls) -> Iterator[dict[str, str]]:
        for config in cls.LOADED:
            yield config.get_description()

    @classmethod
    def load_configuration(cls) -> None:
        pass


@dataclass
class CSVConfig(BaseConfig):
    CONFIG_TYPE = 'csv-config'

    carrier: str
    dialect: str
    clear_columns: Iterable[str]
    encode_columns: Iterable[str]
    delimiter: Optional[str] = None

    def map_file(self, in_file: FilePath, worker: Worker, destination: io.BufferedWriter) -> None:
        with in_file.open() as source:
            reader, writer = self.csv_reader_writer(source, destination)
            encode = worker.encode_value
            mapper = self.mapper
            writer.writeheader()
            writer.writerows([mapper(row, encode) for row in reader])

    def csv_reader_writer(self, source, dest):
        config = {'dialect': self.dialect}
        if self.delimiter:
            config['delimiter'] = self.delimiter
        reader = csv.DictReader(f=source, **config)
        writer = csv.DictWriter(f=dest, fieldnames=reader.fieldnames, **config)
        return reader, writer

    def mapper(self, d, encode):
        d = d.copy()
        for key in self.clear_columns:
            d[key] = ''
        for key in self.encode_columns:
            d[key] = encode(d.get(key) or '')
        return d

    def get_description(self) -> dict[str, str]:
        return self.make_description(
            f'{self.carrier} - {self.file_mask}',
            f'Configuration for {self.carrier} - {self.file_mask}',
            f'Clear columns: {self.clear_columns or "None"}\nEncode columns: {self.encode_columns or "None"}',
        )


ConfigFactory.LOADED = [
    # Verizon
    CSVConfig(carrier='Verizon', dialect='excel-tab', file_mask='Wireless Usage Detail',
              clear_columns={'ECPD Profile ID', 'Number'},
              encode_columns={'Wireless Number', 'Account Number', 'User Name', 'Invoice Number'}),
    CSVConfig(carrier='Verizon', dialect='excel-tab', file_mask='Acct & Wireless Charges Detail Summary Usage',
              clear_columns={'ECPD Profile ID', 'Vendor Name / Contact Information'},
              encode_columns={'Wireless Number', 'Account Number', 'User Name', 'Invoice Number'}),
    CSVConfig(carrier='Verizon', dialect='excel-tab', file_mask='AccountSummary',
              clear_columns={'ECPD Profile ID', 'Bill Name', 'Remittance Address'},
              encode_columns={'Account Number', 'Invoice Number'}),
    CSVConfig(carrier='Verizon', dialect='excel-tab', file_mask='Account & Wireless Summary',
              clear_columns={'ECPD Profile ID'},
              encode_columns={'Wireless Number', 'Account Number', 'User Name', 'Invoice Number'}),
]


def add_common_arguments(parser, add_mapping):
    parser.add_argument('output_directory', metavar='Output directory', widget='DirChooser',
                        help='Path to store output files')
    if add_mapping:
        parser.add_argument('mapping_file', metavar='Mapping file', widget='FileChooser',
                            help='mapping.tsv file', gooey_options={'wildcard': "Tab separated file (*.tsv)|*.tsv"})

    parser.add_argument('input', action='store', nargs='+', metavar='Input files', widget='MultiFileChooser',
                        help='Files or directories to be processed')


def main():
    parser = GooeyParser(
        description='Program to anonymize data files for Byte Analytics Mobile Optimizer',
        epilog='Run without arguments to launch the GUI',
    )

    subparsers = parser.add_subparsers(dest='action', required=True)
    encode = subparsers.add_parser('Encode', help='Anonymize the data files')
    add_common_arguments(encode, False)

    decode = subparsers.add_parser('Decode', help='De-anonymize the data files')
    add_common_arguments(decode, True)

    args = parser.parse_args()
    assert args.action in ('Encode', 'Decode')
    for_encode = args.action == 'Encode'

    with Worker(args.output_directory, should_save_mappings=for_encode) as worker:
        worker.find_files(args.input, for_encode=for_encode)
        if for_encode and (path := Path(args.output_directory) / 'mapping.tsv').exists():
            worker.load_mappings(path)
        elif not for_encode:
            worker.load_mappings(args.mapping_file)
        worker.process_files()


def get_resource_path(*args):
    if getattr(sys, 'frozen', False):
        # MEIPASS explanation:
        # https://pythonhosted.org/PyInstaller/#run-time-operation
        resource_dir = getattr(sys, '_MEIPASS', None)
    else:
        resource_dir = os.path.normpath(os.path.dirname(__file__))
    return os.path.join(resource_dir, *args)


if __name__ == '__main__':
    ConfigFactory.load_configuration()

    if len(sys.argv) > 1:
        # CLI
        IGNORE_COMMAND = '--ignore-gooey'
        if IGNORE_COMMAND in sys.argv:
            sys.argv.remove(IGNORE_COMMAND)
        main()
    else:
        MENU = [
            {'name': 'Help', 'items': [
                {
                    'type': 'AboutDialog',
                    'menuTitle': 'About',
                    'name': 'Byte Analytics Data Anonymizer',
                    'description': 'Program to anonymize data files for Byte Analytics Mobile Optimizer',
                    'version': 'latest',  # TODO: git tag
                    'copyright': '2021',
                    'website': 'https://github.com/reef-technologies/byteanalytics-anonymizer',
                    'developer': 'https://reef.pl/',
                    'license': 'GPL v3'
                },
                {
                    'type': 'Link',
                    'menuTitle': 'Check for updates',
                    'url': 'https://github.com/reef-technologies/byteanalytics-anonymizer/releases',
                }
            ]},
            {'name': 'Carrier Configuration', 'items': list(ConfigFactory.get_config_descriptions())},
        ]

        # GUI
        Gooey(
            f=main,
            language='english',
            show_sidebar=True,
            program_name='Byte Analytics Data Encoder',
            advanced=True,
            default_size=(900, 600),
            required_cols=1,
            optional_cols=1,
            menu=MENU,
            image_dir=get_resource_path('images'),
            language_dir=get_resource_path('gooey', 'languages'),
            progress_regex=r"^Progress (?P<percent>\d+)%$",
            progress_expr="percent",
            disable_progress_bar_animation=True,
            hide_progress_msg=True,
        )()
