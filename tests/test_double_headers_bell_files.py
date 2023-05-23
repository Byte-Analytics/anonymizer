from anonymizer import BaseConfig, CSVConfig
from tests.config_tester import ConfigTester


class TestDoubleHeaderWithEncoding(ConfigTester):
    def get_file_name(self) -> str:
        return 'bell_double_header_MOB.csv'

    # def get_config(self) -> BaseConfig:
    #     return CSVConfig(
    #         file_mask='_MOB',
    #         carrier='Bell',
    #         dialect='excel',
    #         clear_columns=[],
    #         encode_columns=[
    #             'Acct Nbr',
    #             'Mobile Nbr',
    #             'Surname',
    #             'Given Name',
    #             'Ref Nbr',
    #             'Group Subscriber',
    #             'Category',
    #             'SubCategory',
    #         ],
    #         num_headers=2,
    #         encoding='iso-8859-1',
    #     )
