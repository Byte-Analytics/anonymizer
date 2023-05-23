from anonymizer import FilePath, ZipPath
from tests.config_tester import ConfigTester, CsvDataLoader


class TestRogersCustomFile(ConfigTester, CsvDataLoader):
    def get_file_path(self) -> FilePath:
        return ZipPath(self.data_directory / 'rogers/test_Custom.zip', 'ALL_CALLS-Custom.txt')
