from tests.config_tester import ConfigTester, CsvDataLoader


class TestATnTRawDataOutputFile(ConfigTester, CsvDataLoader):
    def get_file_name(self) -> str:
        return 'at&t/rawdataoutput_test.csv'

    def assert_encoded_data(self, input_encoded_data: list[dict[str, str]]) -> None:
        # We have to ensure that Section_3 was anonymised when Section_2 had value `User Name`.
        for entry in input_encoded_data:
            if entry['Section_2'].strip() == 'User Name':
                assert entry['Section_3'].strip() != 'TEST_USER_NAME'
