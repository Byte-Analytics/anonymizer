import csv
import os
import pathlib
from typing import cast

COLUMNS_TO_REMOVE = [
    'ECPD Profile ID',
    'Bill Name',
    'Remittance Address',
    'Vendor Name / Contact Information',
    'Account Number',
    'User Name',
    'Invoice Number',
    'Number',
    'Cost Center',
]
COLUMNS_TO_ENCODE = ['Wireless Number']


def main() -> None:
    output_dir = pathlib.Path('output')
    if output_dir.exists():
        print('`output` directory already exists. Please remove it and try again.')
        raise SystemExit(1)
    os.mkdir(output_dir)

    encode_mapping = {}

    def get_encoded(value: str) -> str:
        if value not in encode_mapping:
            next_number = f'{len(encode_mapping) + 1:010d}'
            encode_mapping[value] = f'{next_number[:3]}-{next_number[3:6]}-{next_number[6:]}'
        return encode_mapping[value]

    for filename in pathlib.Path('.').glob('*.txt'):
        print(f'Processing {filename}')
        output_filename = output_dir / filename.name

        with open(filename, 'r') as input_file, open(output_filename, 'w') as output_file:
            reader = csv.DictReader(input_file, delimiter='\t')
            fieldnames = [field for field in reader.fieldnames if field not in COLUMNS_TO_REMOVE]
            writer = csv.DictWriter(output_file, delimiter='\t', fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                row = cast(dict, row)
                for column in COLUMNS_TO_REMOVE:
                    if column in row:
                        del row[column]
                for column in COLUMNS_TO_ENCODE:
                    if column in row:
                        row[column] = get_encoded(row[column].strip())
                writer.writerow(row)


if __name__ == '__main__':
    main()
