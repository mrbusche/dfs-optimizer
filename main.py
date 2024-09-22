import pandas as pd
from pulp import LpMaximize, LpProblem, LpVariable, lpSum

# Constants
POSITION = "DK Position"
PROJECTION = "DK Projection"
SALARY = "DK Salary"
PLAYER = "Player"

SALARY_CAP = 50000
MAX_LINEUPS = 10

lineup_configs = {
    "four_wr": {"QB": 1, "RB": 2, "WR": 4, "TE": 1, "DST": 1},
    "three_rb": {"QB": 1, "RB": 3, "WR": 3, "TE": 1, "DST": 1},
    "two_te": {"QB": 1, "RB": 2, "WR": 3, "TE": 2, "DST": 1}
}

players = pd.read_csv("draftkings.csv", usecols=[PLAYER, POSITION, PROJECTION, SALARY])
# trim whitespace from columns
players = players.apply(lambda x: x.str.strip() if x.dtype == "object" else x)


# Group players by position
available_players = players.groupby([POSITION, PLAYER, PROJECTION, SALARY]).size().reset_index()

# Create salary and points dicts by position
salaries = {
    pos: available_players[available_players[POSITION] == pos].set_index(PLAYER)[SALARY].to_dict()
    for pos in available_players[POSITION].unique()
}
points = {
    pos: available_players[available_players[POSITION] == pos].set_index(PLAYER)[PROJECTION].to_dict()
    for pos in available_players[POSITION].unique()
}

def calculate_lineups(lineup_type, output_file):
    total_score = 0
    lineup_results = []

    for lineup_num in range(1, MAX_LINEUPS + 1):
        player_vars = {pos: LpVariable.dicts(pos, players, cat="Binary") for pos, players in points.items()}

        prob = LpProblem("Fantasy", LpMaximize)
        prob += lpSum([points[pos][player] * player_vars[pos][player] for pos in player_vars for player in player_vars[pos]])
        prob += lpSum([salaries[pos][player] * player_vars[pos][player] for pos in player_vars for player in player_vars[pos]]) <= SALARY_CAP

        # Enforce lineup constraints (how many players from each position)
        for pos, count in lineup_type.items():
            prob += lpSum([player_vars[pos][player] for player in player_vars[pos]]) == count

        # Ensure each new lineup has a lower score than the previous
        if lineup_num > 1:
            prob += lpSum([points[pos][player] * player_vars[pos][player] for pos in player_vars for player in player_vars[pos]]) <= total_score - 0.001

        prob.solve()

        lineup = {
            "Lineup #": lineup_num
        }
        total_score = 0
        total_salary = 0
        column_count = 1

        for pos in player_vars:
            for player, var in player_vars[pos].items():
                if var.varValue == 1:
                    # Adding player details in a structured way for each position
                    lineup[f"Player {column_count} Position"] = pos
                    lineup[f"Player {column_count} Name"] = player
                    lineup[f"Player {column_count} Salary"] = salaries[pos][player]
                    lineup[f"Player {column_count} Projected Points"] = points[pos][player]
                    total_score += points[pos][player]
                    total_salary += salaries[pos][player]
                    column_count += 1

        lineup["Total Salary"] = total_salary
        lineup["Total Score"] = '{0:.1f}'.format(total_score)
        lineup_results.append(lineup)

    pd.DataFrame(lineup_results).to_csv(output_file + ".csv", index=False, header=False)

# Calculate lineups for each configuration
for lineup_name, lineup_type in lineup_configs.items():
    calculate_lineups(lineup_type, lineup_name)

print("Lineup files created")
