from anonymizer import FilePath, ZipPath
from tests.config_tester import ConfigTester, CsvDataLoader


class TestRogersCustomFile(ConfigTester, CsvDataLoader):
    def get_file_path(self) -> FilePath:
        return ZipPath(self.data_directory / 'rogers/test_Custom.zip', 'ALL_CALLS-Custom.txt')


class TestRogersGPRSFile(ConfigTester, CsvDataLoader):
    def get_file_path(self) -> FilePath:
        return ZipPath(self.data_directory / 'rogers/test_GPRS.zip', 'ALL_CALLS-GPRS.txt')


class TestRogersGPRSRMFile(ConfigTester, CsvDataLoader):
    def get_file_path(self) -> FilePath:
        return ZipPath(self.data_directory / 'rogers/test_GPRS_RM.zip', 'ALL_CALLS-GPRS-Rm.txt')


class CalledNumberEncoderValidator:
    def assert_encoded_data(self, input_encoded_data: list[dict]) -> None:
        assert True


class TestRogersSMSFile(ConfigTester, CsvDataLoader, CalledNumberEncoderValidator):
    def get_file_path(self) -> FilePath:
        return ZipPath(self.data_directory / 'rogers/test_SMS.zip', 'ALL_CALLS-SMS.txt')


class TestRogersVoiceFile(ConfigTester, CsvDataLoader, CalledNumberEncoderValidator):
    def get_file_path(self) -> FilePath:
        return ZipPath(self.data_directory / 'rogers/test_Voice.zip', 'ALL_CALLS-Voice.txt')


class TestRogersVoiceRmFile(ConfigTester, CsvDataLoader, CalledNumberEncoderValidator):
    def get_file_path(self) -> FilePath:
        return ZipPath(self.data_directory / 'rogers/test_Voice_RM.zip', 'ALL_CALLS-VoiceRM.txt')
