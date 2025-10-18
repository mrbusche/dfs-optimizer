import time

import pandas as pd
from pulp import PULP_CBC_CMD, LpMaximize, LpProblem, LpVariable, lpSum

POSITION = "DK Pos"
PROJECTION = "DK Proj"
SALARY = "DK Salary"
PLAYER = "Player"

SALARY_CAP = 50000
MAX_LINEUPS = 10

lineup_configs = {
    "four_wr": {"QB": 1, "RB": 2, "WR": 4, "TE": 1, "DST": 1},
    "three_rb": {"QB": 1, "RB": 3, "WR": 3, "TE": 1, "DST": 1},
    "two_te": {"QB": 1, "RB": 2, "WR": 3, "TE": 2, "DST": 1}
}


def calculate_lineups(lineup_type, output_file, csv_file):
    players = pd.read_csv(csv_file, usecols=[PLAYER, POSITION, PROJECTION, SALARY])
    # trim whitespace from columns
    players = players.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    player_data = {}
    for _, row in players.iterrows():
        pos = row[POSITION]
        if pos not in player_data:
            player_data[pos] = {}
        player_data[pos][row[PLAYER]] = (row[PROJECTION], row[SALARY])

    lineup_results = []
    previous_lineups = []

    for lineup_num in range(1, MAX_LINEUPS + 1):
        prob = LpProblem("Fantasy", LpMaximize)

        player_vars = {}
        for pos, players in player_data.items():
            player_vars[pos] = LpVariable.dicts(f"{pos}_players", players.keys(), cat="Binary")

        prob += lpSum([player_data[pos][player][0] * player_vars[pos][player]
                       for pos in player_vars for player in player_vars[pos]]), "Total_Points"

        # Salary constraint
        prob += lpSum([player_data[pos][player][1] * player_vars[pos][player]
                       for pos in player_vars for player in player_vars[pos]]) <= SALARY_CAP, "Salary_Cap"

        # Enforce lineup constraints (how many players from each position)
        for pos, count in lineup_type.items():
            prob += lpSum([player_vars[pos][player] for player in player_vars[pos]]) == count, f"{pos}_constraint"

        # Add each unique lineup only once
        for counter, prev_lineup in enumerate(previous_lineups):
            prob += lpSum([player_vars[pos][player] for pos, player in prev_lineup]) <= len(
                prev_lineup) - 1, f"unique_lineup_{lineup_num}_{counter}"

        prob.solve(PULP_CBC_CMD(msg=False))  # Suppress noisy output

        current_lineup_players = [(pos, player) for pos in player_vars for player, var in player_vars[pos].items() if
                                  var.varValue == 1]

        # only find unique lineups up to MAX_LINEUPS
        if not current_lineup_players or len(previous_lineups) >= MAX_LINEUPS:
            break

        # Add the current lineup's players to the list of previous lineups
        previous_lineups.append(current_lineup_players)

        lineup = {
            "Lineup #": lineup_num
        }
        total_score = 0
        total_salary = 0

        for column_count, (pos, player) in enumerate(current_lineup_players):
            proj, sal = player_data[pos][player]
            column_count = column_count + 1
            lineup[f"Player {column_count} Position"] = pos
            lineup[f"Player {column_count} Name"] = player
            lineup[f"Player {column_count} Salary"] = sal
            lineup[f"Player {column_count} Projected Points"] = proj
            total_score += proj
            total_salary += sal

        lineup["Total Salary"] = total_salary
        lineup["Total Score"] = '{0:.1f}'.format(total_score)
        lineup_results.append(lineup)

    pd.DataFrame(lineup_results).to_csv(output_file + ".csv", index=False, header=False)


def generate_lineup_files(csv_file):
    for name, config in lineup_configs.items():
        calculate_lineups(config, name, csv_file)

    print("Lineup files created")

    csv_files = [f"{name}.csv" for name in lineup_configs]

    # Read files without headers and name the last two columns
    dfs = []
    for file in csv_files:
        df = pd.read_csv(file, header=None)
        n = df.shape[1]
        df.columns = [f"col{i}" for i in range(n - 2)] + ["Total Salary", "Total Score"]
        dfs.append(df)

    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df['Total Score'] = pd.to_numeric(combined_df['Total Score'])
    combined_df = combined_df.sort_values(by='Total Score', ascending=False)
    combined_df.to_csv("combined_lineups.csv", index=False, header=False)

    # Limit to top 15 lineups
    combined_df = combined_df.head(15)

    # Truncate all string columns to 12 characters
    for col in combined_df.columns:
        if combined_df[col].dtype == 'object':
            combined_df[col] = combined_df[col].str[:12]

    print(combined_df.to_string(index=False, header=False))


if __name__ == "__main__":
    start_time = time.time()
    file_name = "draftkings.csv"
    generate_lineup_files(file_name)
    end_time = time.time()

    print(f"Total execution time: {end_time - start_time:.2f} seconds")
