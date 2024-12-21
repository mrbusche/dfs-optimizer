import os

import pytest

from main import generate_lineup_files


@pytest.fixture(autouse=True)
def generate_files():
    generate_lineup_files('./tests/draftkings.csv')


def test_generate_lineup_files():
    assert os.path.exists('four_wr.csv')
    assert os.path.exists('three_rb.csv')
    assert os.path.exists('two_te.csv')


def test_four_wr():
    with open('four_wr.csv', 'r') as f:
        four_wr = [f.readline().strip() for _ in range(10)]

    # because of the duplicate scores, the results are not always returned in the same order
    conditions = [
        len(four_wr) == 10,
        four_wr[0][-5:] == "145.5",
        four_wr[1][-5:] == "145.3",
        four_wr[2][-5:] == "145.3",
        four_wr[3][-5:] == "145.3",
        four_wr[4][-5:] == "145.3",
        four_wr[5][-5:] == "145.3",
        four_wr[6][-5:] == "145.2",
        four_wr[7][-5:] == "145.2",
        four_wr[8][-5:] == "145.2",
        four_wr[9][-5:] == "145.2",
    ]

    assert all(conditions)


def test_three_rb():
    with open('three_rb.csv', 'r') as f:
        three_rb = [f.readline().strip() for _ in range(10)]

    conditions = [
        len(three_rb) == 10,
        three_rb[0][-5:] == "148.2",
        three_rb[1][-5:] == "148.0",
        three_rb[2][-5:] == "148.0",
        three_rb[3][-5:] == "147.9",
        three_rb[4][-5:] == "147.9",
        three_rb[5][-5:] == "147.9",
        three_rb[6][-5:] == "147.8",
        three_rb[7][-5:] == "147.8",
        three_rb[8][-5:] == "147.8",
        three_rb[9][-5:] == "147.7",
    ]

    assert all(conditions)


def test_two_te():
    with open('two_te.csv', 'r') as f:
        two_te = [f.readline().strip() for _ in range(10)]

    conditions = [
        len(two_te) == 10,
        two_te[0][-5:] == "146.0",
        two_te[1][-5:] == "146.0",
        two_te[2][-5:] == "146.0",
        two_te[3][-5:] == "145.9",
        two_te[4][-5:] == "145.9",
        two_te[5][-5:] == "145.8",
        two_te[6][-5:] == "145.8",
        two_te[7][-5:] == "145.7",
        two_te[8][-5:] == "145.7",
        two_te[9][-5:] == "145.7",
    ]

    assert all(conditions)
