# https://www.youtube.com/watch?v=zibV6xaOGEA

import pandas as pd
from pulp import LpProblem, LpMaximize, LpVariable, lpSum
import openpyxl
import os

players = pd.read_csv(
    r"draftkings.csv", usecols=["Player", "DK Position", "DK Projection", "DK Salary"],
)

wb = openpyxl.Workbook()
ws = wb.active

available_players = players.groupby(
    ["DK Position", "Player", "DK Projection", "DK Salary"]
).agg("count")
available_players = available_players.reset_index()

salaries = {}
points = {}

for pos in available_players["DK Position"].unique():
    available_pos = available_players[available_players["DK Position"] == pos]
    salary = list(
        available_pos[["Player", "DK Salary"]].set_index("Player").to_dict().values()
    )[0]
    point = list(
        available_pos[["Player", "DK Projection"]]
        .set_index("Player")
        .to_dict()
        .values()
    )[0]

    salaries[pos] = salary
    points[pos] = point

four_wr = {"QB": 1, "RB": 2, "WR": 4, "TE": 1, "DST": 1}
three_rb = {"QB": 1, "RB": 3, "WR": 3, "TE": 1, "DST": 1}
two_te = {"QB": 1, "RB": 2, "WR": 3, "TE": 2, "DST": 1}

salary_cap = 50000
max_rows = 15


def calculate(lineup_type, file_name):
    total_score = 0
    for lineup in range(1, max_rows + 1):
        _vars = {k: LpVariable.dict(k, v, cat="Binary") for k, v in points.items()}

        prob = LpProblem("Fantasy", LpMaximize)
        rewards = []
        costs = []

        for k, v in _vars.items():
            costs += lpSum([salaries[k][i] * _vars[k][i] for i in v])
            rewards += lpSum([points[k][i] * _vars[k][i] for i in v])
            prob += lpSum([_vars[k][i] for i in v]) == lineup_type[k]

        prob += lpSum(rewards)
        prob += lpSum(costs) <= salary_cap
        if lineup != 1:
            prob += lpSum(rewards) <= total_score - 0.001
        prob.solve()

        score = str(prob.objective)
        column_number = 1

        for v in prob.variables():
            score = score.replace(v.name, str(v.varValue))
            if v.varValue != 0:
                ws.cell(row=lineup, column=column_number).value = v.name
                column_number += 1

        total_score = eval(score)
        ws.cell(row=lineup, column=column_number).value = total_score

    wb.save(file_name + ".xlsx")
    pd.read_excel(file_name + ".xlsx").to_csv(file_name + ".csv", index=False)


calculate(three_rb, "three_rb")
calculate(four_wr, "four_wr")
calculate(two_te, "two_te")

path = os.getcwd()
if os.path.isfile(path + "\\combined.csv"):
    os.remove(path + "\\combined.csv")

file_list = [path + "\\four_wr.csv", path + "\\three_rb.csv", path + "\\two_te.csv"]
print("file_list", file_list)
excl_list = []

# for file in file_list:
for idx, file in enumerate(file_list):
    excl_list.append(pd.read_csv(file))  # , header=0 if idx == 0 else None

# excl_merged = pd.DataFrame()

# for excl_file in excl_list:
#     excl_merged = pd.concat([excl_merged, excl_file], ignore_index=False)

# excl_merged.to_csv("combined.csv")
