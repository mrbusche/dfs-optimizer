import importlib.util
from pathlib import Path

import pandas as pd
import pytest

MODULE_PATH = Path(__file__).parents[1] / 'marry-salaries.py'
SPEC = importlib.util.spec_from_file_location('marry_salaries', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
marry_salaries = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(marry_salaries)


@pytest.mark.parametrize(
    ('position', 'dk_value', 'dk_salary', 'extracted_salary', 'expected'),
    [
        ('QB', 1.4, 8000, 7600, 2.6),
        ('RB', 7.0, 8800, 9300, 6.0),
        ('WR', 0.3, 8600, 9300, -1.1),
        ('TE', 0.9, 6700, 6200, 1.9),
        ('DST', 0.7, 2500, 2600, 0.5),
        ('RB', 7.0, 8800, 8800, 7.0),
    ],
)
def test_calculate_extracted_value(position, dk_value, dk_salary, extracted_salary, expected):
    assert marry_salaries.calculate_extracted_value(dk_value, dk_salary, extracted_salary, position) == expected


def test_calculate_extracted_value_rejects_unknown_position():
    with pytest.raises(ValueError, match='Unsupported DraftKings position: K'):
        marry_salaries.calculate_extracted_value(1.0, 5000, 5000, 'K')


def test_match_dfs_players_prints_unchanged_values_above_negative_one(tmp_path, capsys):
    dk_file = tmp_path / 'projections.csv'
    salaries_file = tmp_path / 'salaries.csv'
    output_file = tmp_path / 'matched.csv'
    pd.DataFrame(
        [
            {'Player': 'Positive Same', 'DK Salary': 5000, 'DK Value': 4.0, 'DK Pos': 'RB'},
            {'Player': 'Zero Same', 'DK Salary': 5000, 'DK Value': 0.0, 'DK Pos': 'RB'},
            {'Player': 'Negative Same', 'DK Salary': 5000, 'DK Value': -0.5, 'DK Pos': 'RB'},
            {'Player': 'Boundary Same', 'DK Salary': 5000, 'DK Value': -1.0, 'DK Pos': 'RB'},
            {'Player': 'Higher Value', 'DK Salary': 5000, 'DK Value': 2.0, 'DK Pos': 'RB'},
        ]
    ).to_csv(dk_file, index=False)
    pd.DataFrame(
        [
            {'Name': 'Positive Same', 'Salary': 5000},
            {'Name': 'Zero Same', 'Salary': 5000},
            {'Name': 'Negative Same', 'Salary': 5000},
            {'Name': 'Boundary Same', 'Salary': 5000},
            {'Name': 'Higher Value', 'Salary': 4500},
        ]
    ).to_csv(salaries_file, index=False)

    marry_salaries.match_dfs_players(str(dk_file), str(salaries_file), str(output_file))

    output = capsys.readouterr().out
    assert 'Players with unchanged positive Value:' in output
    assert 'Positive Same: Extracted Value=4.0, DK Value=4.0' in output
    assert 'Zero Same: Extracted Value=0.0, DK Value=0.0' in output
    assert 'Negative Same: Extracted Value=-0.5, DK Value=-0.5' in output
    assert 'Boundary Same:' not in output
    assert 'Players with higher Extracted Value:\nHigher Value: Extracted Value=3.0, DK Value=2.0' in output
