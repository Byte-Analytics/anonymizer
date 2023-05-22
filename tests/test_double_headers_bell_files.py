import pathlib

from anonymizer import CSVConfig, EncodeItem


def test_load_double_header(mock_worker):
    in_file = pathlib.Path(__file__).parent / 'data' / 'bell_double_header_MOB.csv'
    config = CSVConfig(
        file_mask='_MOB',
        carrier='Bell',
        dialect='excel',
        clear_columns=[],
        encode_columns=[
            'Acct Nbr',
            'Mobile Nbr',
            'Surname',
            'Given Name',
            'Ref Nbr',
            'Group Subscriber',
            'Category',
            'SubCategory',
        ],
        num_headers=2,
        encoding='iso-8859-1',
    )

    encode_item = EncodeItem(path=in_file, config=config)
    encode_item.process(mock_worker)

    mock_worker.save_output.assert_called_once()
    output_data = mock_worker.save_output.call_args.args[1]
    assert output_data == in_file.read_bytes()
