import pytest

from anonymizer import EncodeRegex, TableEncodeRegex


@pytest.mark.parametrize(
    ','.join(['expression', 'input_str', 'expected']),
    [
        ('^(?P<t1>[a-z0-9]+) -- (?P<t2>[a-z0-9]+)$', 'abc -- 123', 'cba -- 321'),
        ('^(?P<t1>[a-z0-9]+) (?P<t2>[a-z0-9]+)$', 'testvalue1 testvalue2', '1eulavtset 2eulavtset'),
        ('^.* (?P<user_number>[0-9]+)$', 'User number in the end 1234', 'User number in the end 4321'),
    ]
)
def test_encode_regex_reverse(expression: str, input_str: str, expected: str) -> None:
    def encoder(in_str: str) -> str:
        return in_str[::-1]

    output = EncodeRegex(expression).encode(input_str, encoder)
    assert output == expected


@pytest.mark.parametrize(
    ','.join(['expression', 'replacement', 'input_str', 'expected']),
    [
        (
            '^(?P<t1>[a-z]+) test text (?P<t2>[a-z-]+)',
            {'text': 'a very long text', 'long-word': 't'},
            'text test text long-word',
            'a very long text test text t',
        )
    ]
)
def test_encode_regex_replacement(expression: str, replacement: dict[str, str], input_str: str, expected: str) -> None:
    output = TableEncodeRegex(expression, 'dummy-column').encode(input_str, replacement.get)
    assert output == expected
