import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).parents[1] / 'marry-salaries.py'
SPEC = importlib.util.spec_from_file_location('marry_salaries', MODULE_PATH)
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
    assert (
        marry_salaries.calculate_extracted_value(dk_value, dk_salary, extracted_salary, position) == expected
    )


def test_calculate_extracted_value_rejects_unknown_position():
    with pytest.raises(ValueError, match='Unsupported DraftKings position: K'):
        marry_salaries.calculate_extracted_value(1.0, 5000, 5000, 'K')
