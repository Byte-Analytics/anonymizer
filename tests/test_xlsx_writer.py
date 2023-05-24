import pathlib

from openpyxl.reader.excel import load_workbook

from anonymizer import XlsxReader, XlsxWriter


def test_xlsx_writer(fake_fs):
    in_file = pathlib.Path(__file__).parent / 'data/bell/test-Hardware report.xlsx'
    input_workbook = load_workbook(in_file, read_only=True, rich_text=True)  # noqa: rich_text missing from pyi
    input_worksheet = input_workbook.active

    header = ['test1', 'test2', 'test3']
    data = [
        ['value1', 'value2', 'value3'],
        ['value4', 'value5', 'value6'],
        ['value7', 'value8', 'value9'],
    ]

    writer = XlsxWriter(input_worksheet, fieldnames=['test1', 'test2', 'test3'])
    writer.writeheader()
    for data_line in data:
        mapping = dict(zip(header, data_line))
        writer.writerow(mapping)

    output_file = 'test.xlsx'
    with open(output_file, 'wb') as f:
        writer.save_workbook(f)

    # At this point it is assumed that reader is "ok".
    output_workbook = load_workbook(output_file, read_only=True, rich_text=True)  # noqa: rich_text missing from pyi
    output_worksheet = output_workbook.active

    reader = XlsxReader(worksheet=output_worksheet)
    for idx, line_dict in enumerate(reader):
        expected_line = dict(zip(header, data[idx]))
        assert line_dict == expected_line
