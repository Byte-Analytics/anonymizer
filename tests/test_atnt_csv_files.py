from anonymizer import FilePath
from tests.config_tester import ConfigTester, TableDataLoader


class TestATnTRawDataOutputFile(ConfigTester, TableDataLoader):
    def get_file_path(self) -> FilePath:
        return self.data_directory / 'at&t/rawdataoutput_test.csv'

    def assert_encoded_data(self, input_encoded_data: list[dict[str, str]], _file: FilePath) -> None:
        # We have to ensure that Section_3 was anonymized when Section_2 had value `User Name`.
        for entry in input_encoded_data:
            if entry['Section_2'].strip() == 'User Name':
                assert entry['Section_3'].strip() != 'TEST_USER_NAME'
