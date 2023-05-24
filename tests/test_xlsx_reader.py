import pathlib

from openpyxl.reader.excel import load_workbook

from anonymizer import XlsxReader


def test_read_xlsx_file() -> None:
    in_file = pathlib.Path(__file__).parent / 'data/bell/test-Hardware report.xlsx'
    workbook = load_workbook(in_file, read_only=True, rich_text=True)  # noqa: rich_text missing from pyi
    worksheet = workbook.active

    reader = XlsxReader(worksheet)
    lines = []
    for dict_line in reader:
        lines.append(dict_line)

    assert len(lines) == 3

    # Check some basic fields that we know from this document.
    field_tag_mapping = [
        ('Mobile number', 'test-mobile-{}'),
        ('User last name', 'test-last-{}'),
        ('User first name', 'test-first-{}'),
        ('Model code', 'test-model-{}'),
    ]

    for idx, line_dict in enumerate(lines, start=1):
        for dict_key, format_tag in field_tag_mapping:
            assert line_dict.get(dict_key) == format_tag.format(idx)
