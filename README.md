# dfs-optimizer

Outputs top DK lineups based on a csv file

Add a file named `draftkings.csv` into your root. It must contain the following columns, all other columns are ignored

Columns: `"Player", "DK Pos", "DK Proj", "DK Salary"`

This project use `uv`, [Installing uv](https://docs.astral.sh/uv/getting-started/installation/)

`uv sync`

`python main.py`

3 files will be generated

1. four_wr.csv
2. three_rb.csv
3. two_te.csv

and the top lineups will be output to the console. From there you can pick your poison

## Force Include/Exclude Players

You can force include or exclude specific players from all generated lineups.

### Usage

Edit the `main.py`, `playoff.py`, or `playoff-one-per-team.py` file to specify players:

```python
if __name__ == '__main__':
    # Example: Force include two players and exclude one
    must_include = ['Player Name 1', 'Player Name 2']
    exclude_list = ['Player Name 3']
    
    generate_lineup_files('draftkings.csv', must_include_players=must_include, exclude_players=exclude_list)
```

### Parameters

- `must_include_players`: List of player names to force include in every lineup
- `exclude_players`: List of player names to exclude from all lineups

Both parameters are optional and default to empty lists if not provided.

### Notes

- Player names must match exactly as they appear in the CSV file
- The optimizer will warn if a player name is not found in the CSV
- Must-include constraints are enforced in the optimization, so lineups may not be found if the must-include players violate other constraints (e.g., salary cap)
