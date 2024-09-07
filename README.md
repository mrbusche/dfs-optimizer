# dfs-optimizer

Outputs top DK lineups based on a csv file

Add a file named `draftkings.csv` into your root. It must contain the following columns, all other columns are ignored

Columns: `"Player", "DK Position", "DK Projection", "DK Salary"`

`python -m pip install -r ./requirements.txt`

`python main.py`

3 files will be generated

1. four_wr.csv
2. three_rb.csv
3. two_te.csv

From there you can pick your poison
