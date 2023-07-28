from anonymizer import FilePath
from tests.config_tester import ConfigTester, TableDataLoader


class TestBellMobFile(ConfigTester, TableDataLoader):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'bell/double_header_MOB.csv'


class TestBellAccFile(ConfigTester, TableDataLoader):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'bell/double_header_ACC.csv'


class TestBellDtlFile(ConfigTester, TableDataLoader):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'bell/double_header_DTL.csv'
