import pandas as pd

from main import (
    LineupConfig,
    OptimizationParams,
    Player,
    calculate_lineups,
    validate_players_data,
)


def make_players() -> list[Player]:
    return [
        Player(name='Allowed QB', position='QB', salary=5000, projection=20),
        Player(name='Other QB', position='QB', salary=5000, projection=19),
        Player(name='Allowed RB 1', position='RB', salary=5000, projection=15),
        Player(name='Allowed RB 2', position='RB', salary=5000, projection=14),
        Player(name='Other RB', position='RB', salary=5000, projection=13),
        Player(name='Allowed WR 1', position='WR', salary=5000, projection=15),
        Player(name='Allowed WR 2', position='WR', salary=5000, projection=14),
        Player(name='Allowed WR 3', position='WR', salary=5000, projection=13),
        Player(name='Other WR', position='WR', salary=5000, projection=30),
        Player(name='Allowed TE', position='TE', salary=5000, projection=12),
        Player(name='Other TE', position='TE', salary=5000, projection=11),
        Player(name='DST', position='DST', salary=5000, projection=10),
    ]


def test_validate_players_data_uses_extracted_salary_column():
    players = validate_players_data(
        pd.DataFrame(
            [
                {
                    'Player': 'Test Player',
                    'DK Pos': 'QB',
                    'DK Salary': '$7,800',
                    'DK Proj': '18.5',
                }
            ]
        )
    )

    assert players == [Player(name='Test Player', position='QB', salary=7800, projection=18.5)]


def test_optimization_params_maps_position_restrictions_and_converts_none():
    params = OptimizationParams(only_use_qb=None, only_use_rb=['Allowed RB 1'])

    assert params.position_only_use_map() == {
        'QB': [],
        'RB': ['Allowed RB 1'],
        'WR': [],
        'TE': [],
    }


def test_position_only_use_restriction_applies_to_non_flex_slots(tmp_path):
    lineup = calculate_lineups(
        LineupConfig(QB=1, RB=2, WR=3, TE=1, DST=1),
        str(tmp_path / 'standard'),
        make_players(),
        OptimizationParams(only_use_qb=['Allowed QB']),
    )

    assert lineup
    assert all(player.name == 'Allowed QB' for result in lineup for player in result.players if player.position == 'QB')


def test_position_only_use_restriction_leaves_flex_slot_open(tmp_path):
    lineup = calculate_lineups(
        LineupConfig(QB=1, RB=2, WR=4, TE=1, DST=1),
        str(tmp_path / 'four_wr'),
        make_players(),
        OptimizationParams(only_use_wr=['Allowed WR 1', 'Allowed WR 2', 'Allowed WR 3']),
    )

    assert lineup
    for result in lineup:
        wide_receivers = {player.name for player in result.players if player.position == 'WR'}
        assert len(wide_receivers & {'Allowed WR 1', 'Allowed WR 2', 'Allowed WR 3'}) >= 3

    assert any(player.name == 'Other WR' for result in lineup for player in result.players if player.position == 'WR')
