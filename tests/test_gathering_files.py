import pathlib
import zipfile

from anonymizer import Worker


def test_gathering_files(fake_fs) -> None:
    data_path = pathlib.Path(__file__).parent / 'data'

    with Worker('.') as worker:
        worker.find_files([data_path], for_encode=True)
        gathered_files = set(str(entry.path) for entry in worker.queue)

    all_files = []
    for file_path in data_path.glob('**/*'):
        if file_path.name.startswith('.') or not file_path.is_file():
            continue

        if file_path.suffix == '.zip':
            zip_path = zipfile.Path(file_path, at='')
            all_files.extend(str(elem) for elem in zip_path.iterdir())
        else:
            all_files.append(str(file_path))

    assert gathered_files == set(all_files)
