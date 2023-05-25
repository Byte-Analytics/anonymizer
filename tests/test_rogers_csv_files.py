from anonymizer import ENC_PATTERN, FilePath, ZipPath
from tests.config_tester import ConfigTester, TableDataLoader


class TestRogersCustomFile(ConfigTester, TableDataLoader):
    def get_file_path(self) -> FilePath:
        return ZipPath(self.data_directory / 'rogers/test_Custom.zip', 'ALL_CALLS-Custom.txt')


class TestRogersGPRSFile(ConfigTester, TableDataLoader):
    def get_file_path(self) -> FilePath:
        return ZipPath(self.data_directory / 'rogers/test_GPRS.zip', 'ALL_CALLS-GPRS.txt')


class TestRogersGPRSRMFile(ConfigTester, TableDataLoader):
    def get_file_path(self) -> FilePath:
        return ZipPath(self.data_directory / 'rogers/test_GPRS_RM.zip', 'ALL_CALLS-GPRS-Rm.txt')


class CalledNumberEncoderValidator:
    def assert_encoded_data(self, input_encoded_data: list[dict], _encoded_file: FilePath) -> None:
        for line_dict in input_encoded_data:
            called_number = line_dict['Called Number']
            assert called_number == '*' or ENC_PATTERN.match(called_number), f'{called_number}'


class TestRogersSMSFile(ConfigTester, TableDataLoader, CalledNumberEncoderValidator):
    def get_file_path(self) -> FilePath:
        return ZipPath(self.data_directory / 'rogers/test_SMS.zip', 'ALL_CALLS-SMS.txt')


class TestRogersVoiceFile(ConfigTester, TableDataLoader, CalledNumberEncoderValidator):
    def get_file_path(self) -> FilePath:
        return ZipPath(self.data_directory / 'rogers/test_Voice.zip', 'ALL_CALLS-Voice.txt')


class TestRogersVoiceRmFile(ConfigTester, TableDataLoader, CalledNumberEncoderValidator):
    def get_file_path(self) -> FilePath:
        return ZipPath(self.data_directory / 'rogers/test_Voice_RM.zip', 'ALL_CALLS-VoiceRM.txt')
