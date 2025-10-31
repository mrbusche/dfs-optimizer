import os
import tempfile

import pandas as pd
import pytest

from main import calculate_lineups, generate_lineup_files


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
        four_wr[0][-5:] == '145.5',
        four_wr[1][-5:] == '145.3',
        four_wr[2][-5:] == '145.3',
        four_wr[3][-5:] == '145.3',
        four_wr[4][-5:] == '145.3',
        four_wr[5][-5:] == '145.3',
        four_wr[6][-5:] == '145.2',
        four_wr[7][-5:] == '145.2',
        four_wr[8][-5:] == '145.2',
        four_wr[9][-5:] == '145.2',
    ]

    assert all(conditions)


def test_three_rb():
    with open('three_rb.csv', 'r') as f:
        three_rb = [f.readline().strip() for _ in range(10)]

    conditions = [
        len(three_rb) == 10,
        three_rb[0][-5:] == '148.2',
        three_rb[1][-5:] == '148.0',
        three_rb[2][-5:] == '148.0',
        three_rb[3][-5:] == '147.9',
        three_rb[4][-5:] == '147.9',
        three_rb[5][-5:] == '147.9',
        three_rb[6][-5:] == '147.8',
        three_rb[7][-5:] == '147.8',
        three_rb[8][-5:] == '147.8',
        three_rb[9][-5:] == '147.7',
    ]

    assert all(conditions)


def test_two_te():
    with open('two_te.csv', 'r') as f:
        two_te = [f.readline().strip() for _ in range(10)]

    conditions = [
        len(two_te) == 10,
        two_te[0][-5:] == '146.0',
        two_te[1][-5:] == '146.0',
        two_te[2][-5:] == '146.0',
        two_te[3][-5:] == '145.9',
        two_te[4][-5:] == '145.9',
        two_te[5][-5:] == '145.8',
        two_te[6][-5:] == '145.8',
        two_te[7][-5:] == '145.7',
        two_te[8][-5:] == '145.7',
        two_te[9][-5:] == '145.7',
    ]

    assert all(conditions)


def test_must_include_players():
    """Test that must-include players appear in all generated lineups"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        output_file = f.name.replace('.csv', '')

    try:
        must_include = ['Lamar Jackson']
        df = pd.read_csv('./tests/draftkings.csv')
        calculate_lineups(
            {'QB': 1, 'RB': 2, 'WR': 3, 'TE': 1, 'DST': 1},
            output_file,
            df,
            must_include_players=must_include,
            only_use_players=[],
        )

        df = pd.read_csv(output_file + '.csv', header=None)

        # Check that Lamar Jackson appears in every lineup
        for _, row in df.iterrows():
            row_str = ','.join(row.astype(str))
            assert 'Lamar Jackson' in row_str, "Must-include player 'Lamar Jackson' not found in lineup"
    finally:
        if os.path.exists(output_file + '.csv'):
            os.remove(output_file + '.csv')


def test_only_use_players():
    """Test that only specified players are used when only_use_players is provided"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        output_file = f.name.replace('.csv', '')

    try:
        # Include enough players from each position to form a valid lineup
        only_use = [
            'Lamar Jackson',
            'Josh Allen',  # QBs
            'Derrick Henry',
            'Saquon Barkley',
            'Alvin and the Chipmunks',  # RBs
            'CeeDee Lamb',
            "Ja'Marr Chase",
            'Tyreek Hill',
            'Chris Olave',  # WRs
            'Trey McBride',
            'Mike Gesicki',  # TEs
            'Ravens',
            'Titans',
        ]  # DSTs

        df = pd.read_csv('./tests/draftkings.csv')
        calculate_lineups(
            {'QB': 1, 'RB': 2, 'WR': 3, 'TE': 1, 'DST': 1},
            output_file,
            df,
            must_include_players=[],
            only_use_players=only_use,
        )

        df = pd.read_csv(output_file + '.csv', header=None)

        # Verify at least one lineup was generated with the restricted player pool
        assert len(df) > 0, 'No lineups generated with only_use_players restriction'

        # Parse the lineup to check that only specified players are used
        for _, row in df.iterrows():
            row_str = ','.join(row.astype(str))
            # Check for some players that should NOT be in the output
            assert 'Jayden Daniels' not in row_str, 'Player not in only_use list found in lineup'
            assert 'Joe Burrow' not in row_str, 'Player not in only_use list found in lineup'
    finally:
        if os.path.exists(output_file + '.csv'):
            os.remove(output_file + '.csv')


def test_salary_cap_constraint():
    """Test that all generated lineups stay under the salary cap"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        output_file = f.name.replace('.csv', '')

    try:
        df = pd.read_csv('./tests/draftkings.csv')
        calculate_lineups({'QB': 1, 'RB': 2, 'WR': 3, 'TE': 1, 'DST': 1}, output_file, df)

        df = pd.read_csv(output_file + '.csv', header=None)

        # The second to last column should be Total Salary
        for _, row in df.iterrows():
            total_salary = row.iloc[-2]  # Second to last column
            assert total_salary <= 50000, f'Lineup exceeds salary cap: ${total_salary}'
    finally:
        if os.path.exists(output_file + '.csv'):
            os.remove(output_file + '.csv')


def test_missing_must_include_player_warning(capsys):
    """Test that warnings are printed when must-include players are not found"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        output_file = f.name.replace('.csv', '')

    try:
        must_include = ['NonExistentPlayer123']
        df = pd.read_csv('./tests/draftkings.csv')
        calculate_lineups(
            {'QB': 1, 'RB': 2, 'WR': 3, 'TE': 1, 'DST': 1},
            output_file,
            df,
            must_include_players=must_include,
            only_use_players=[],
        )

        captured = capsys.readouterr()
        assert 'WARNING: Must-include players not found in CSV' in captured.out
        assert 'NonExistentPlayer123' in captured.out
    finally:
        if os.path.exists(output_file + '.csv'):
            os.remove(output_file + '.csv')


def test_missing_only_use_player_warning(capsys):
    """Test that warnings are printed when only-use players are not found"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        output_file = f.name.replace('.csv', '')

    try:
        # Include valid players plus one invalid one to test the warning
        only_use = [
            'NonExistentPlayer456',
            'Lamar Jackson',
            'Josh Allen',
            'Derrick Henry',
            'Saquon Barkley',
            'Alvin and the Chipmunks',
            'CeeDee Lamb',
            "Ja'Marr Chase",
            'Tyreek Hill',
            'Chris Olave',
            'Trey McBride',
            'Mike Gesicki',
            'Ravens',
            'Titans',
        ]
        df = pd.read_csv('./tests/draftkings.csv')
        calculate_lineups(
            {'QB': 1, 'RB': 2, 'WR': 3, 'TE': 1, 'DST': 1},
            output_file,
            df,
            must_include_players=[],
            only_use_players=only_use,
        )

        captured = capsys.readouterr()
        assert 'WARNING: Only-use players not found in CSV' in captured.out
        assert 'NonExistentPlayer456' in captured.out
    finally:
        if os.path.exists(output_file + '.csv'):
            os.remove(output_file + '.csv')


def test_combined_lineups_sorted():
    """Test that combined lineups are sorted by Total Score in descending order"""
    generate_lineup_files('./tests/draftkings.csv')

    df = pd.read_csv('combined_lineups.csv', header=None)
    n = df.shape[1]
    df.columns = [f'col{i}' for i in range(n - 2)] + ['Total Salary', 'Total Score']

    # Convert Total Score to numeric for comparison
    df['Total Score'] = pd.to_numeric(df['Total Score'])

    # Check that scores are in descending order
    scores = df['Total Score'].tolist()
    assert scores == sorted(scores, reverse=True), 'Combined lineups not sorted by score in descending order'


def test_generate_lineup_files_creates_combined(capsys):
    """Test that generate_lineup_files creates combined_lineups.csv and prints output"""
    generate_lineup_files('./tests/draftkings.csv')

    # Check that combined_lineups.csv exists
    assert os.path.exists('combined_lineups.csv'), 'combined_lineups.csv not created'

    # Check console output
    captured = capsys.readouterr()
    assert 'Lineup files created' in captured.out

    # Verify the combined file has content
    df = pd.read_csv('combined_lineups.csv', header=None)
    assert len(df) > 0, 'combined_lineups.csv is empty'


def test_string_truncation_in_output(capsys):
    """Test that strings are truncated to 12 characters in the printed output"""
    generate_lineup_files('./tests/draftkings.csv')

    captured = capsys.readouterr()
    output_lines = captured.out.split('\n')

    # Find lines that contain lineup data - should have multiple columns
    for line in output_lines:
        if line.strip() and not any(keyword in line for keyword in ['Lineup files created', 'execution time']):
            fields = line.split()
            # Check string fields for truncation (skip numeric fields)
            for field in fields:
                # Try to convert to float - if it fails, it's a string field
                try:
                    float(field)
                except ValueError:
                    # It's a string field, check length
                    assert len(field) <= 12, f"Field '{field}' exceeds 12 characters"


def test_unique_lineups_generated():
    """Test that multiple unique lineups are generated"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        output_file = f.name.replace('.csv', '')

    try:
        df = pd.read_csv('./tests/draftkings.csv')
        calculate_lineups({'QB': 1, 'RB': 2, 'WR': 3, 'TE': 1, 'DST': 1}, output_file, df)

        df = pd.read_csv(output_file + '.csv', header=None)

        # Check that multiple lineups were generated (up to MAX_LINEUPS = 10)
        assert len(df) > 1, 'Only one lineup generated, should have multiple unique lineups'

        # Convert each row to a string and check for uniqueness
        lineup_strings = set()
        for _, row in df.iterrows():
            lineup_str = ','.join(row.astype(str))
            assert lineup_str not in lineup_strings, 'Duplicate lineup found'
            lineup_strings.add(lineup_str)
    finally:
        if os.path.exists(output_file + '.csv'):
            os.remove(output_file + '.csv')


def test_position_constraints():
    """Test that lineups respect position constraints"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        output_file = f.name.replace('.csv', '')

    try:
        lineup_config = {'QB': 1, 'RB': 3, 'WR': 3, 'TE': 1, 'DST': 1}
        df = pd.read_csv('./tests/draftkings.csv')
        calculate_lineups(
            lineup_config,
            output_file,
            df,
            must_include_players=[],
            only_use_players=[],
        )

        df = pd.read_csv(output_file + '.csv', header=None)

        # Each lineup should have exactly 9 players (sum of position counts)
        # The CSV has position/name/salary/projection for each player (4 columns per player)
        # Plus lineup number, total salary, and total score
        expected_player_count = sum(lineup_config.values())

        for _, row in df.iterrows():
            # Count player entries (every 4 columns starting from column 1)
            # Column 0 is lineup number, then groups of 4 for each player, then 2 for totals
            player_columns = len(row) - 3  # Subtract lineup #, total salary, total score
            player_count = player_columns // 4
            assert player_count == expected_player_count, (
                f'Expected {expected_player_count} players, found {player_count}'
            )
    finally:
        if os.path.exists(output_file + '.csv'):
            os.remove(output_file + '.csv')
