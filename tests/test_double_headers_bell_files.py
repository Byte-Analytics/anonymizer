from tests.config_tester import ConfigTester


class TestDoubleHeaderWithEncoding(ConfigTester):
    def get_file_name(self) -> str:
        return 'bell/double_header_MOB.csv'
