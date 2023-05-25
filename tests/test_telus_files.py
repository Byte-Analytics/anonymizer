import re

from anonymizer import BaseConfig, FilePath, RawRegexConfig
from tests.config_tester import ConfigTester, DataLoaderProtocol


class RegexDataLoader(DataLoaderProtocol):
    def load_data_for_comparison(self, in_file: FilePath, config: BaseConfig) -> list[dict]:
        assert isinstance(config, RawRegexConfig)
        out_lines = []
        with in_file.open(mode='r', encoding=config.encoding) as source:  # noqa
            for line in source:
                out_line_dict = {}
                for regex in config.regex_groups:
                    match = re.search(regex.expression, line)
                    if match is None:
                        continue
                    out_line_dict[regex.expression] = match.groupdict()
                out_lines.append(out_line_dict)

        return out_lines


class TelusRegexTester:
    SPECIAL_KEYS = [
        # Account related.
        '11223344',
        '112233445566',
        # Phone numbers.
        '1122334455',
        '2233445566',
        '3344556677',
        '4455667788',
        '6677889900',
        '1234567890',
        # Usernames and other special names.
        'test-value-1',
        'test-value-2',
        'test device 1',
        'test device 2',
        'test device 3',
        'test-dept-1',
        'test-cost-1',
        'test-dept-2',
        'test-cost-2',
        'test-device-1',
        'test-device-2',
        'test-device-3',
        'test-device-4',
        'test-device-5',
        'test-device-6',
    ]

    def assert_encoded_data(self, _input_encoded_data: list[dict], file_path: FilePath) -> None:
        with file_path.open(mode='r') as source:
            file_data = source.read()

        for special_key in self.SPECIAL_KEYS:
            assert special_key not in file_data, f'Found {special_key} in {file_path} –\n{file_data}'


class TestTelusAccountDetailFile(ConfigTester, RegexDataLoader, TelusRegexTester):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'telus/Account_Detail_test.txt'


class TestTelusAirtimeDetailFile(ConfigTester, RegexDataLoader, TelusRegexTester):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'telus/Airtime_Detail_test.txt'


class TestTelusDEWReportFile(ConfigTester, RegexDataLoader, TelusRegexTester):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'telus/DEW_Report_test.txt'


class TestTelusGroupSummaryFile(ConfigTester, RegexDataLoader, TelusRegexTester):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'telus/Group_Summary_Report_test.txt'


class TestTelusIndividualDetailFile(ConfigTester, RegexDataLoader, TelusRegexTester):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'telus/Individual_Detail_test.txt'


class TestTelusInvoiceSummaryFile(ConfigTester, RegexDataLoader, TelusRegexTester):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'telus/Invoice_Summary_test.txt'
