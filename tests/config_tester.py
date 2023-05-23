import csv
import pathlib
from typing import Any

from anonymizer import BaseConfig, CSVConfig, ConfigFactory, DecodeItem, EncodeItem, FilePath, Worker, ZipPath


class DataLoaderProtocol:
    def load_data_for_comparison(self, in_file: FilePath, config: BaseConfig) -> Any:
        raise NotImplementedError


class CsvDataLoader(DataLoaderProtocol):
    def load_data_for_comparison(self, in_file: FilePath, config: BaseConfig) -> Any:
        assert isinstance(config, CSVConfig)
        with in_file.open(mode='r', encoding=config.encoding) as f:  # noqa
            reader = csv.DictReader(f, **config.csv_config())  # noqa
            out_lines = []
            for line_dict in reader:
                out_line_dict = {
                    key: value
                    for key, value in line_dict.items()
                    if key.strip() not in config.clear_columns
                }
                out_lines.append(out_line_dict)
        return out_lines


class ConfigTester(DataLoaderProtocol):
    def get_file_name(self) -> str:
        raise NotImplementedError

    def assert_encoded_data(self, input_encoded_data: Any) -> None:
        pass

    def test_encode_decode(self, fake_fs):
        input_file_path = pathlib.Path(self.get_file_name())
        in_file = pathlib.Path(__file__).parent / 'data' / input_file_path
        encoded_file = pathlib.Path(__file__).parent / 'encoded.zip'
        out_file = pathlib.Path(__file__).parent / 'output.zip'

        config = ConfigFactory.get_config(input_file_path.name)
        assert config is not None, f'Unable to match config to {input_file_path.name}'

        original_content = self.load_data_for_comparison(in_file, config)

        with Worker(
                output_directory=str(encoded_file.parent),
                output_zipname=encoded_file.name,
                should_save_mappings=True,
        ) as encode_worker:
            encode_item = EncodeItem(path=in_file, config=config)
            encode_item.process(encode_worker)
            encode_worker.save_mappings()

        encoded_content = self.load_data_for_comparison(ZipPath(encoded_file, input_file_path.name), config)
        assert encoded_content != original_content
        self.assert_encoded_data(encoded_content)

        with Worker(
                output_directory=str(out_file.parent),
                output_zipname=out_file.name,
                should_save_mappings=False,
        ) as decode_worker:
            decode_worker.load_mappings(encoded_file.parent / decode_worker.MAPPING_FILE_NAME)
            decode_item = DecodeItem(path=ZipPath(encoded_file, input_file_path.name), config=config)
            decode_item.process(decode_worker)

        encode_decode_content = self.load_data_for_comparison(ZipPath(out_file, input_file_path.name), config)
        assert encode_decode_content == original_content, f'\n{encode_decode_content}\nvs\n{original_content}'
