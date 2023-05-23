import pathlib

from anonymizer import BaseConfig, ConfigFactory, DecodeItem, EncodeItem, Worker, ZipPath


class ConfigTester:
    def get_file_name(self) -> str:
        raise NotImplementedError

    def get_config(self) -> BaseConfig:
        return ConfigFactory.get_config(self.get_file_name())

    def test_load_double_header(self, fake_fs):
        in_file = pathlib.Path(__file__).parent / 'data' / self.get_file_name()
        encoded_file = pathlib.Path(__file__).parent / 'encoded.zip'
        out_file = pathlib.Path(__file__).parent / 'output.zip'
        config = self.get_config()

        original_content = in_file.read_bytes()

        with Worker(
                output_directory=str(encoded_file.parent),
                output_zipname=encoded_file.name,
                should_save_mappings=True,
        ) as encode_worker:
            encode_item = EncodeItem(path=in_file, config=config)
            encode_item.process(encode_worker)
            encode_worker.save_mappings()

        encoded_content = ZipPath(encoded_file, self.get_file_name()).read_bytes()
        assert encoded_content != original_content

        with Worker(
                output_directory=str(out_file.parent),
                output_zipname=out_file.name,
                should_save_mappings=False,
        ) as decode_worker:
            decode_worker.load_mappings(encoded_file.parent / decode_worker.MAPPING_FILE_NAME)
            decode_item = DecodeItem(path=ZipPath(encoded_file, self.get_file_name()), config=config)
            decode_item.process(decode_worker)

        encode_decode_content = ZipPath(out_file, self.get_file_name()).read_bytes()
        assert encode_decode_content == original_content, \
            f'{encode_decode_content=} vs {original_content=}'
