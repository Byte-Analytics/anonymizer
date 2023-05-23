from tests.config_tester import ConfigTester, CsvDataLoader


class TestBellMobFile(ConfigTester, CsvDataLoader):
    def get_file_name(self) -> str:
        return 'bell/double_header_MOB.csv'


class TestBellAccFile(ConfigTester, CsvDataLoader):
    def get_file_name(self) -> str:
        return 'bell/double_header_ACC.csv'


class TestBellDtlFile(ConfigTester, CsvDataLoader):
    def get_file_name(self) -> str:
        return 'bell/double_header_DTL.csv'
