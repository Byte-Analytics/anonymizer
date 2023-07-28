import pathlib

from anonymizer import ConfigFactory, Operation, QueueItem, Worker


def test_multifile_workflow(fake_fs) -> None:
    in_files = [file_path for file_path in (pathlib.Path(__file__).parent / 'data/telus/').glob('*.txt')]
    encoded_file = pathlib.Path(__file__).parent / 'encoded.zip'

    # Going through all the files and encoding all of them.
    with Worker(
            output_directory=str(encoded_file.parent),
            output_zipname=encoded_file.name,
            should_save_mappings=True,
    ) as encode_worker:
        for file_path in in_files:
            config = ConfigFactory.get_config(file_path.name)
            encode_item = QueueItem(path=file_path, config=config, operation=Operation.ENCODE)
            encode_item.process(encode_worker)
        encode_worker.save_mappings()

        # Loading mapping. This isn't something you normally do.
        mapping_file = encode_worker.output_directory / encode_worker.MAPPING_FILE_NAME
        encode_worker.load_mappings(mapping_file)

        mapping = encode_worker.encoded_mappings

    # Checking the mapping for duplicates.
    assert len(set(mapping.keys())) == len(set(mapping.values()))
