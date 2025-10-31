from __future__ import annotations

import time
from collections.abc import Sequence
from pathlib import Path

import pandas as pd
from pulp import PULP_CBC_CMD, LpMaximize, LpProblem, LpVariable, lpSum

POSITION = 'DK Pos'
PROJECTION = 'DK Proj'
SALARY = 'DK Salary'
PLAYER = 'Player'
TOTAL_SCORE = 'Total Score'

SALARY_CAP = 50000
MAX_LINEUPS = 10

lineup_configs = {
    'four_wr': {'QB': 1, 'RB': 2, 'WR': 4, 'TE': 1, 'DST': 1},
    'three_rb': {'QB': 1, 'RB': 3, 'WR': 3, 'TE': 1, 'DST': 1},
    'two_te': {'QB': 1, 'RB': 2, 'WR': 3, 'TE': 2, 'DST': 1},
}


def calculate_lineups(
    lineup_type: dict[str, int],
    output_file: str,
    all_players_df: pd.DataFrame,
    must_include_players: Sequence[str] | None = None,
    only_use_players: Sequence[str] | None = None,
) -> list[dict]:
    must_include_players = list(must_include_players or [])
    only_use_players = list(only_use_players or [])

    players = all_players_df.copy()
    players = players.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
    players[SALARY] = pd.to_numeric(
        players[SALARY].astype(str).str.removeprefix('$').str.replace(',', '', regex=False), errors='coerce'
    )
    players = players.dropna(subset=[SALARY, PROJECTION])

    # --- Player Filtering ---
    if must_include_players:
        print(f'Must-include players requested: {", ".join(must_include_players)}')
    if only_use_players:
        print(f'Only-use player pool requested: {", ".join(only_use_players)}')

    all_players_set = set(all_players_df[PLAYER])
    missing_must_include = sorted(set(must_include_players) - all_players_set)
    if missing_must_include:
        print(f'WARNING: Must-include players not found in CSV: {", ".join(missing_must_include)}')
    missing_only_use = sorted(set(only_use_players) - all_players_set) if only_use_players else []
    if missing_only_use:
        print(f'WARNING: Only-use players not found in CSV: {", ".join(missing_only_use)}')

    if only_use_players:
        players = players[players[PLAYER].isin(only_use_players)]

    remaining_players_set = set(players[PLAYER])
    unmet_must_include = sorted(set(must_include_players) - remaining_players_set)
    if unmet_must_include:
        print(f'WARNING: Filtered pool missing must-include players: {", ".join(unmet_must_include)}')
    if players.empty:
        print('WARNING: No eligible players remain after filtering; skipping lineup generation.')
        return []

    player_data = {}
    for _, row in players.iterrows():
        pos = row[POSITION]
        if pos not in player_data:
            player_data[pos] = {}
        player_data[pos][row[PLAYER]] = (row[PROJECTION], row[SALARY])

    lineup_results = []
    previous_lineups = []

    for lineup_num in range(1, MAX_LINEUPS + 1):
        prob = LpProblem(f'Fantasy_{output_file}_{lineup_num}', LpMaximize)

        player_vars = {}
        for pos, pos_players in player_data.items():
            player_vars[pos] = LpVariable.dicts(f'{pos}_players', pos_players.keys(), cat='Binary')

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
        for pos, count in lineup_type.items():
            prob += lpSum([player_vars[pos][player] for player in player_vars[pos]]) == count, f'{pos}_constraint'

        # Enforce must-include players
        for must_include in must_include_players:
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

        prob.solve(PULP_CBC_CMD(msg=False))  # Suppress noisy output

        current_lineup_players = [
            (pos, player) for pos in player_vars for player, var in player_vars[pos].items() if var.varValue == 1
        ]

        if not current_lineup_players or len(previous_lineups) >= MAX_LINEUPS:
            break

        previous_lineups.append(current_lineup_players)

        lineup = {'Lineup #': lineup_num}
        total_score = 0
        total_salary = 0

        for column_count, (pos, player) in enumerate(current_lineup_players):
            proj, sal = player_data[pos][player]
            column_count += 1
            lineup[f'Player {column_count} Position'] = pos
            lineup[f'Player {column_count} Name'] = player
            lineup[f'Player {column_count} Salary'] = sal
            lineup[f'Player {column_count} Projected Points'] = proj
            total_score += proj
            total_salary += sal

        lineup['Total Salary'] = total_salary
        lineup[TOTAL_SCORE] = f'{total_score:.1f}'
        lineup_results.append(lineup)

    # Write the individual file (as required by README/tests)
    output_path = Path(output_file)
    if output_path.suffix != '.csv':
        output_path = output_path.with_suffix('.csv')
    pd.DataFrame(lineup_results).to_csv(output_path, index=False, header=False)

    return lineup_results


def generate_lineup_files(
    csv_file: str | Path,
    must_include_players: Sequence[str] | None = None,
    only_use_players: Sequence[str] | None = None,
) -> None:
    csv_path = Path(csv_file)

    try:
        players_df = pd.read_csv(csv_path, usecols=[PLAYER, POSITION, PROJECTION, SALARY])
        players_df = players_df.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
        players_df[SALARY] = pd.to_numeric(
            players_df[SALARY].astype(str).str.removeprefix('$').str.replace(',', '', regex=False), errors='coerce'
        )
        players_df = players_df.dropna(subset=[SALARY, PROJECTION])
    except FileNotFoundError:
        print(f"Error: Input file '{csv_path}' not found.")
        return
    except ValueError as e:
        print(f'Error processing {csv_path}: {e}')
        return

    all_lineups_results = []
    for name, config in lineup_configs.items():
        # Pass the pre-processed DataFrame to the calculation function
        lineups = calculate_lineups(
            config,
            name,
            players_df,
            must_include_players,
            only_use_players,
        )
        all_lineups_results.extend(lineups)

    print('Lineup files created')

    if not all_lineups_results:
        print('No lineups were generated.')
        return

    combined_df = pd.DataFrame(all_lineups_results)

    combined_df[TOTAL_SCORE] = pd.to_numeric(combined_df[TOTAL_SCORE])
    combined_df = combined_df.sort_values(by=TOTAL_SCORE, ascending=False)
    combined_df.to_csv(Path('combined_lineups.csv'), index=False, header=False)

    # Limit to top 15 lineups for printing
    combined_df_print = combined_df.head(15).copy()

    # Truncate all string columns to 12 characters for printing
    for col in combined_df_print.columns:
        if combined_df_print[col].dtype == 'object':
            combined_df_print.loc[:, col] = combined_df_print[col].str[:12]

    print(combined_df_print.to_string(index=False, header=False))


if __name__ == '__main__':
    start_time = time.time()
    file_name = Path('draftkings.csv')

    # Specify players that must be included in all lineups
    must_include = []

    # Specify the only players that can be used (empty list = use all players)
    only_use = []

    generate_lineup_files(file_name, must_include, only_use)
    end_time = time.time()

    print(f'Total execution time: {end_time - start_time:.2f} seconds')
