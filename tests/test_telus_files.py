from anonymizer import FilePath
from tests.config_tester import ConfigTester


class TestTelusAccountDetailFile(ConfigTester):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'telus/Account_Detail_test.txt'


class TestTelusAirtimeDetailFile(ConfigTester):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'telus/Airtime_Detail_test.txt'


class TestTelusDEWReportFile(ConfigTester):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'telus/DEW_Report_test.txt'


class TestTelusGroupSummaryFile(ConfigTester):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'telus/Group_Summary_Report_test.txt'


class TestTelusIndividualDetailFile(ConfigTester):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'telus/Individual_Detail_test.txt'


class TestTelusInvoiceSummaryFile(ConfigTester):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'telus/Invoice_Summary_test.txt'
