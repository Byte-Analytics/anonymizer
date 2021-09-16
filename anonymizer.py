#!/usr/bin/env python3
"""
Used to anonymize real tsv/csv files, keeping mapping between original and anonymized data so that process
can be reversed on optimized files.

Unlike scripts/transform-csv.py which was this based on, file type configuration is hardcoded, so that
users are protected from configuration mistakes.
"""
import collections
import csv
import sys
import zipfile
import random
import re
import functools
from pathlib import Path
import codecs
import io

from dataclasses import dataclass
from typing import Iterable, Optional

from gooey import Gooey, GooeyParser

ENCODED_DIGITS = 16


def random_digits():
    return ''.join(str(random.randint(0, 9)) for _ in range(ENCODED_DIGITS))


class Encoder:
    input_directory: Path
    output_directory: Path
    encoded_mappings: dict[str, str]
    encoded_values: set[str]
    output_zipfile: zipfile.ZipFile
    output_zipname: str

    def __init__(self, input_directory, output_directory, output_zipname=None):
        self.input_directory = Path(input_directory)
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self.encoded_mappings = {}
        self.encoded_values = set()
        self.processed_count = 0
        self.output_zipname = output_zipname or 'output.zip'  # TODO: timestamped name by default?

    @functools.cached_property
    def output_zipfile(self):
        return zipfile.ZipFile(self.output_directory / self.output_zipname, mode="w")  # TODO: options?

    def encode(self, value):
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

    def process_file(self, source, relative_path, config):
        dest = io.StringIO()
        reader, writer = config.csv_reader_writer(source, dest)
        encode = self.encode
        writer.writeheader()
        writer.writerows(config.mapper(row, encode) for row in reader)
        data = dest.getvalue().encode('utf-8')
        self.output_zipfile.writestr(str(relative_path), data)
        self.processed_count += 1

    def process_zip(self, path: Path):
        print(f'Processing ZIP {path}')

        with zipfile.ZipFile(path) as input_archive:
            for name in input_archive.namelist():
                config = FormatConfig.get_config(name)
                if config is not None:
                    print(f'  Processing {path}/{name}')
                    with input_archive.open(name) as content:
                        source = codecs.getreader('utf-8')(content)
                        self.process_file(source, path.relative_to(self.input_directory) / name, config)
                else:
                    print(f'  Skipping {path}/{name}')

    def process_dir(self, path):
        print(f'Processing directory {path}')
        for p in path.iterdir():
            self.process(p)

    def process(self, path):
        if path.is_dir():
            self.process_dir(path)
        elif path.is_file() and path.suffix.lower().endswith('.zip'):
            self.process_zip(path)
        else:
            config = FormatConfig.get_config(path.name)
            if config is not None:
                print(f'Processing file {path}')
                with open(path, "r", encoding='utf-8') as source:
                    self.process_file(source, path.relative_to(self.input_directory), config)
            else:
                print(f'Skipping file {path}')

    def finish(self):
        print(f'Successfully processed {self.processed_count} data files')
        if self.processed_count:
            self.output_zipfile.close()
            self.save_mappings()

    def save_mappings(self):
        # TODO: write to temp and rename?
        with open(self.output_directory / 'mapping.tsv', mode="w", encoding='utf-8') as f:
            writer = csv.writer(f, dialect='excel-tab')
            writer.writerows(self.encoded_mappings.items())

    def load_mappings(self):
        with open(self.output_directory / 'mapping.tsv', mode="r", encoding='utf-8') as f:
            reader = csv.reader(f, dialect='excel-tab')
            self.encoded_mappings = dict(reader)
            self.encoded_values = set(self.encoded_mappings.values())


@dataclass
class FormatConfig:
    carrier: str
    dialect: str
    file_mask: str
    clear_columns: Iterable[str]
    encode_columns: Iterable[str]
    delimiter: Optional[str] = None

    def matches(self, filename, flags=0):
        return re.match(self.file_mask, filename, flags=flags)

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

    @classmethod
    def get_config(cls, filename):
        return next((config for config in cls.CONFIGS if config.matches(filename)), None)

    @classmethod
    def get_config_descriptions(cls):
        carriers = collections.defaultdict(list)
        for config in cls.CONFIGS:
            yield {
                'type': 'MessageDialog',
                'menuTitle': f'{config.carrier} - {config.file_mask}',
                'caption': f'Configuration for {config.carrier} - {config.file_mask}',
                'message': f'Clear columns: {config.clear_columns or "None"}\n'
                           f'Encode columns: {config.encode_columns or "None"}'
            }


FormatConfig.CONFIGS = [
    # AT&T
    FormatConfig(carrier='AT&T', dialect='excel-tab', delimiter='|', file_mask='rawdataoutput',
                 clear_columns={'Number Called To/From'},
                 encode_columns={'Foundation Account Name', 'Billing Account Name', 'Wireless Number'}
                 ),
    # Verizon
    FormatConfig(carrier='Verizon', dialect='excel-tab', file_mask='Wireless Usage Detail',
                 clear_columns={'ECPD Profile ID'},
                 encode_columns={'Wireless Number', 'Account Number', 'User Name', 'Invoice Number', 'Number'}),
    FormatConfig(carrier='Verizon', dialect='excel-tab', file_mask='Acct & Wireless Charges Detail Summary Usage',
                 clear_columns={'ECPD Profile ID', 'Vendor Name / Contact Information'},
                 encode_columns={'Wireless Number', 'Account Number', 'User Name', 'Invoice Number'}),
    FormatConfig(carrier='Verizon', dialect='excel-tab', file_mask='AccountSummary',
                 clear_columns={'ECPD Profile ID', 'Bill Name', 'Remittance Address'},
                 encode_columns={'Account Number', 'Invoice Number'}),
    FormatConfig(carrier='Verizon', dialect='excel-tab', file_mask='Account & Wireless Summary',
                 clear_columns={'ECPD Profile ID'},
                 encode_columns={'Wireless Number', 'Account Number', 'User Name', 'Invoice Number'}),
]

MENU = [
    {'name': 'Help', 'items': [
        {
            'type': 'AboutDialog',
            'menuTitle': 'About',
            'name': 'Byte Analytics Data Anonymizer',
            'description': 'Program to anonymize data files for Byte Analytics Mobile Optimizer',
            'version': 'latest',
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
    {'name': 'Carrier Configuration', 'items': list(FormatConfig.get_config_descriptions())},

]


def main():
    parser = GooeyParser(
        description='Program to anonymize data files for Byte Analytics Mobile Optimizer',
        epilog='Run without arguments to launch the GUI',
    )
    subparsers = parser.add_subparsers(dest='action')
    encode = subparsers.add_parser('Encode', help='Anonymize the data files')
    encode.add_argument('input_directory', metavar='Input directory', widget='DirChooser',
                        help='Path containing files (ZIP/TSV/CSV) to be processed (anonymized)')
    encode.add_argument('output_directory', metavar='Output directory', widget='DirChooser',
                        help='Path to store output files')

    decode = subparsers.add_parser('Decode', help='De-anonymize the data files')
    decode.add_argument('mapping_file', metavar='Mapping file', widget='FileChooser',
                        help='mapping.tsv file')
    decode.add_argument('data_files', metavar='Data files', widget='MultiFileChooser',
                        help='Data files to de-anonymize')

    args = parser.parse_args()
    # print(args)
    if args.action == 'Encode':
        worker = Encoder(args.input_directory, args.output_directory)
        worker.process_dir(worker.input_directory)
        worker.finish()
    else:
        pass


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # CLI
        IGNORE_COMMAND = '--ignore-gooey'
        if IGNORE_COMMAND in sys.argv:
            sys.argv.remove(IGNORE_COMMAND)
        main()
    else:
        # GUI
        Gooey(
            f=main,
            show_sidebar=True,
            program_name='Byte Analytics Data Encoder',
            advanced=True,
            default_size=(900, 600),
            required_cols=1,
            optional_cols=1,
            menu=MENU
        )()
