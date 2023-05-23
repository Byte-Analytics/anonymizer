from anonymizer import FilePath
from tests.config_tester import ConfigTester, CsvDataLoader


class TestVerizonAccountAndWirelessSummaryFile(ConfigTester, CsvDataLoader):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'verizon/Account & Wireless Summary_test.txt'


class TestVerizonAccountSummaryFile(ConfigTester, CsvDataLoader):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'verizon/AccountSummary_test.txt'


class TestVerizonAcctAndWirelessChargesDetailsFile(ConfigTester, CsvDataLoader):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'verizon/Acct & Wireless Charges Detail Summary Usage_test.txt'


class TestVerizonWirelessUsageDetailFile(ConfigTester, CsvDataLoader):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'verizon/Wireless Usage Detail_test.txt'
