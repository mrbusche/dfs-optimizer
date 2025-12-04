from __future__ import annotations

import time
from collections.abc import Sequence
from pathlib import Path

import pandas as pd
from pulp import PULP_CBC_CMD, LpMaximize, LpProblem, LpVariable, lpSum
from pydantic import BaseModel, ConfigDict, Field, field_validator

POSITION = 'DK Pos'
PROJECTION = 'DK Proj'
SALARY = 'DK Salary'
PLAYER = 'Player'
TOTAL_SCORE = 'Total Score'

SALARY_CAP = 50000
MAX_LINEUPS = 10


class Player(BaseModel):
    """Represents a single player with their stats"""

    name: str = Field(..., min_length=1)
    position: str = Field(..., min_length=1)
    salary: int = Field(..., ge=0, le=SALARY_CAP)
    projection: float = Field(..., ge=0)

    @field_validator('position')
    def validate_position(cls, v):
        valid_positions = {'QB', 'RB', 'WR', 'TE', 'DST'}
        if v not in valid_positions:
            raise ValueError(f'Position must be one of {valid_positions}')
        return v


class LineupConfig(BaseModel):
    """Represents the configuration for a lineup type"""

    model_config = ConfigDict(populate_by_name=True)

    qb: int = Field(..., ge=0, le=3, alias='QB')
    rb: int = Field(..., ge=0, le=4, alias='RB')
    wr: int = Field(..., ge=0, le=5, alias='WR')
    te: int = Field(..., ge=0, le=3, alias='TE')
    dst: int = Field(..., ge=0, le=2, alias='DST')

    def total_players(self) -> int:
        return self.qb + self.rb + self.wr + self.te + self.dst


class LineupPlayer(BaseModel):
    """Represents a player in a lineup"""

    position: str
    name: str
    salary: int
    projected_points: float


class Lineup(BaseModel):
    """Represents a complete lineup"""

    lineup_number: int = Field(..., ge=1)
    players: list[LineupPlayer] = Field(..., min_length=1)
    total_salary: int = Field(..., ge=0, le=SALARY_CAP)
    total_score: float = Field(..., ge=0)

    @field_validator('total_salary')
    def validate_salary_cap(cls, v):
        if v > SALARY_CAP:
            raise ValueError(f'Total salary {v} exceeds salary cap {SALARY_CAP}')
        return v

    def to_dict(self) -> dict:
        """Convert to dictionary format for CSV output"""
        result = {'Lineup #': self.lineup_number}

        for i, player in enumerate(self.players, 1):
            result[f'Player {i} Position'] = player.position
            result[f'Player {i} Name'] = player.name
            result[f'Player {i} Salary'] = player.salary
            result[f'Player {i} Projected Points'] = player.projected_points

        result['Total Salary'] = self.total_salary
        result[TOTAL_SCORE] = f'{self.total_score:.1f}'

        return result


class OptimizationParams(BaseModel):
    """Parameters for lineup optimization"""

    must_include_players: list[str] = Field(default_factory=list)
    only_use_players: list[str] = Field(default_factory=list)
    exclude_players: list[str] = Field(default_factory=list)

    @field_validator('must_include_players', 'only_use_players', 'exclude_players', mode='before')
    @classmethod
    def convert_none_to_empty_list(cls, v):
        return v if v is not None else []


lineup_configs = {
    'four_wr': LineupConfig(QB=1, RB=2, WR=4, TE=1, DST=1),
    'three_rb': LineupConfig(QB=1, RB=3, WR=3, TE=1, DST=1),
    'two_te': LineupConfig(QB=1, RB=2, WR=3, TE=2, DST=1),
}


def validate_players_data(df: pd.DataFrame) -> list[Player]:
    """Validate and convert DataFrame to list of Player models"""
    players = []

    for _, row in df.iterrows():
        try:
            # Convert salary from string to int
            salary_str = str(row[SALARY]).replace('$', '').replace(',', '')
            salary = int(float(salary_str))

            player = Player(
                name=str(row[PLAYER]).strip(),
                position=str(row[POSITION]).strip(),
                salary=salary,
                projection=float(row[PROJECTION]),
            )
            players.append(player)
        except (ValueError, KeyError) as e:
            print(f'Warning: Skipping invalid player data: {e}')
            continue

    return players


def calculate_lineups(
    lineup_config: LineupConfig,
    output_file: str,
    players: list[Player],
    params: OptimizationParams,
) -> list[Lineup]:
    """Calculate optimal lineups using Pydantic models"""

    # Validate parameters
    all_player_names = {p.name for p in players}

    missing_must_include = sorted(set(params.must_include_players) - all_player_names)
    if missing_must_include:
        print(f'WARNING: Must-include players not found in CSV: {", ".join(missing_must_include)}')

    missing_only_use = sorted(set(params.only_use_players) - all_player_names) if params.only_use_players else []
    if missing_only_use:
        print(f'WARNING: Only-use players not found in CSV: {", ".join(missing_only_use)}')

    missing_exclude = sorted(set(params.exclude_players) - all_player_names) if params.exclude_players else []
    if missing_exclude:
        print(f'WARNING: Exclude players not found in CSV: {", ".join(missing_exclude)}')

    # Filter players based on parameters
    filtered_players = players

    if params.only_use_players:
        filtered_players = [p for p in filtered_players if p.name in params.only_use_players]

    if params.exclude_players:
        filtered_players = [p for p in filtered_players if p.name not in params.exclude_players]

    remaining_player_names = {p.name for p in filtered_players}
    unmet_must_include = sorted(set(params.must_include_players) - remaining_player_names)
    if unmet_must_include:
        print(f'WARNING: Filtered pool missing must-include players: {", ".join(unmet_must_include)}')

    if not filtered_players:
        print('WARNING: No eligible players remain after filtering; skipping lineup generation.')
        return []

    # Group players by position
    player_data = {}
    for player in filtered_players:
        if player.position not in player_data:
            player_data[player.position] = {}
        player_data[player.position][player.name] = (player.projection, player.salary)

    lineup_results = []
    previous_lineups = []

    for lineup_num in range(1, MAX_LINEUPS + 1):
        prob = LpProblem(f'Fantasy_{output_file}_{lineup_num}', LpMaximize)

        player_vars = {}
        for pos, players_dict in player_data.items():
            player_vars[pos] = LpVariable.dicts(f'{pos}_players', players_dict.keys(), cat='Binary')

        prob += (
            lpSum(
                [
                    player_data[pos][player][0] * player_vars[pos][player]
                    for pos in player_vars
                    for player in player_vars[pos]
                ]
            ),
            'Total_Points',
        )

        # Salary constraint
        prob += (
            lpSum(
                [
                    player_data[pos][player][1] * player_vars[pos][player]
                    for pos in player_vars
                    for player in player_vars[pos]
                ]
            )
            <= SALARY_CAP,
            'Salary_Cap',
        )

        # Enforce lineup constraints (how many players from each position)
        lineup_dict = lineup_config.model_dump(by_alias=True)
        for pos, count in lineup_dict.items():
            if pos in player_vars and count > 0:
                prob += lpSum([player_vars[pos][player] for player in player_vars[pos]]) == count, f'{pos}_constraint'

        # Enforce must-include players
        for must_include in params.must_include_players:
            for pos in player_vars:
                if must_include in player_vars[pos]:
                    prob += player_vars[pos][must_include] == 1, f'must_include_{must_include}'
                    break

        # Add unique lineup constraints
        for counter, prev_lineup in enumerate(previous_lineups):
            prob += (
                lpSum([player_vars[pos][player] for pos, player in prev_lineup]) <= len(prev_lineup) - 1,
                f'unique_lineup_{lineup_num}_{counter}',
            )

        prob.solve(PULP_CBC_CMD(msg=False))

        current_lineup_players = [
            (pos, player) for pos in player_vars for player, var in player_vars[pos].items() if var.varValue == 1
        ]

        if not current_lineup_players or len(previous_lineups) >= MAX_LINEUPS:
            break

        previous_lineups.append(current_lineup_players)

        # Create Lineup object
        lineup_players = []
        total_score = 0
        total_salary = 0

        for pos, player_name in current_lineup_players:
            proj, sal = player_data[pos][player_name]
            lineup_players.append(LineupPlayer(position=pos, name=player_name, salary=sal, projected_points=proj))
            total_score += proj
            total_salary += sal

        try:
            lineup = Lineup(
                lineup_number=lineup_num, players=lineup_players, total_salary=total_salary, total_score=total_score
            )
            lineup_results.append(lineup)
        except ValueError as e:
            print(f'Warning: Invalid lineup generated: {e}')
            continue

    # Write the individual files
    output_path = Path(output_file)
    if output_path.suffix != '.csv':
        output_path = output_path.with_suffix('.csv')

    lineup_dicts = [lineup.to_dict() for lineup in lineup_results]
    pd.DataFrame(lineup_dicts).to_csv(output_path, index=False, header=False)

    return lineup_results


def generate_lineup_files(
    csv_file: str | Path,
    must_include_players: Sequence[str] | None = None,
    only_use_players: Sequence[str] | None = None,
    exclude_players: Sequence[str] | None = None,
    allow_two_te: bool = True,
) -> None:
    csv_path = Path(csv_file)

    try:
        players_df = pd.read_csv(csv_path, usecols=[PLAYER, POSITION, PROJECTION, SALARY])
        players_df = players_df.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
        players_df = players_df.dropna(subset=[SALARY, PROJECTION])
    except FileNotFoundError:
        print(f"Error: Input file '{csv_path}' not found.")
        return
    except ValueError as e:
        print(f'Error processing {csv_path}: {e}')
        return

    # Convert to Player objects with validation
    players = validate_players_data(players_df)

    if not players:
        print('Error: No valid players found in the data.')
        return

    # Create optimization parameters
    params = OptimizationParams(
        must_include_players=list(must_include_players or []),
        only_use_players=list(only_use_players or []),
        exclude_players=list(exclude_players or []),
    )

    # --- Player Filtering ---
    if params.must_include_players:
        print(f'Must-include players requested: {", ".join(params.must_include_players)}')
    if params.only_use_players:
        print(f'Only-use player pool requested: {", ".join(params.only_use_players)}')
    if params.exclude_players:
        print(f'Exclude players requested: {", ".join(params.exclude_players)}')

    all_lineups_results = []
    for name, config in lineup_configs.items():
        if name == 'two_te' and not allow_two_te:
            continue
        lineups = calculate_lineups(config, name, players, params)
        all_lineups_results.extend(lineups)

    print('Lineup files created')

    if not all_lineups_results:
        print('No lineups were generated.')
        return

    # Convert to DataFrame for processing
    lineup_dicts = [lineup.to_dict() for lineup in all_lineups_results]
    combined_df = pd.DataFrame(lineup_dicts)

    combined_df[TOTAL_SCORE] = pd.to_numeric(combined_df[TOTAL_SCORE])
    combined_df = combined_df.sort_values(by=TOTAL_SCORE, ascending=False)
    combined_df.to_csv(Path('combined_lineups.csv'), index=False, header=False)

    # Limit to top 15 lineups for printing
    combined_df_print = combined_df.head(15).copy()

    # Truncate all string columns to 12 characters for printing
    for col in combined_df_print.columns:
        if pd.api.types.is_string_dtype(combined_df_print[col]) or combined_df_print[col].dtype == 'object':
            combined_df_print.loc[:, col] = combined_df_print[col].astype(str).str[:12]

    print(combined_df_print.to_string(index=False, header=False))


if __name__ == '__main__':
    start_time = time.time()
    file_name = Path('draftkings.csv')

    # Specify players that must be included in all lineups
    must_include = []

    # Specify the only players that can be used (empty list = use all players)
    only_use = []

    # Specify players to exclude from all lineups
    exclude = []

    two_te_allowed = True

    generate_lineup_files(file_name, must_include, only_use, exclude, allow_two_te=two_te_allowed)
    end_time = time.time()

    print(f'Total execution time: {end_time - start_time:.2f} seconds')
