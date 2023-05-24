from anonymizer import FilePath
from tests.config_tester import ConfigTester, TableDataLoader


class TestBellCostOverviewFile(ConfigTester, TableDataLoader):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'bell/test-Cost overview.xlsx'


class TestBellEnhancedUserProfileFile(ConfigTester, TableDataLoader):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'bell/test-Enhanced User profile report.xlsx'


class TestBellHardwareFile(ConfigTester, TableDataLoader):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'bell/test-Hardware report.xlsx'


class TestBellInvoiceChargeFile(ConfigTester, TableDataLoader):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'bell/test-Invoice charge report.xlsx'


class TestBellUsageOverviewFile(ConfigTester, TableDataLoader):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'bell/test-Usage overview.xlsx'
