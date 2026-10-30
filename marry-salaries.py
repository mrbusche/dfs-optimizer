import csv
import os
import re
from pathlib import Path

import pandas as pd

NAME_ALIASES = {
    'Nick Singleton': 'Nicholas Singleton',
    'Matt Hibner': 'Matthew Hibner',
    'Mitch Tinsley': 'Mitchell Tinsley',
}

DK_FILE_PREFIX = 'DraftKings NFL DFS Projections -- Main Slate'

SEASON_DFS_PATTERN = 'season-dfs-2026-*.csv'
VALUE_PER_THOUSAND = {'QB': 3, 'RB': 2, 'WR': 2, 'TE': 2, 'DST': 2}


def calculate_extracted_value(dk_value: float, dk_salary: float, extracted_salary: float, position: str) -> float:
    try:
        value_per_thousand = VALUE_PER_THOUSAND[position]
    except KeyError:
        raise ValueError(f'Unsupported DraftKings position: {position}') from None

    return round(dk_value + (dk_salary - extracted_salary) * value_per_thousand / 1000, 1)


def newest_season_dfs_file() -> str:
    downloads_dir = Path.home() / 'Downloads'
    matching_files: list[Path] = [path for path in downloads_dir.glob(SEASON_DFS_PATTERN) if path.is_file()]
    if not matching_files:
        raise FileNotFoundError(f"No file matching '{SEASON_DFS_PATTERN}' found in {downloads_dir}")
    return str(max(matching_files, key=os.path.getmtime))


def export_player_salaries_to_csv(
    input_file: str,
    output_file: str = 'player_salaries.csv',
) -> None:
    season_df = pd.read_csv(input_file)

    records = [
        (
            str(name).strip().rsplit(' ', 1)[-1] if position == 'DST' else str(name).strip(),
            int(salary),
        )
        for name, salary, position in zip(
            season_df['Player Name'],
            season_df['Season DFS Salary'],
            season_df['Position'],
            strict=True,
        )
        if pd.notna(name) and pd.notna(salary)
    ]

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name', 'Salary'])
        writer.writerows(records)

    print(f"Exported {len(records)} entries to '{output_file}'.")


def newest_dk_file() -> str:
    downloads_dir = Path.home() / 'Downloads'
    matching_files: list[Path] = [path for path in downloads_dir.glob(f'{DK_FILE_PREFIX}*') if path.is_file()]
    if not matching_files:
        raise FileNotFoundError(
            f"No DraftKings projection file starting with '{DK_FILE_PREFIX}' found in {downloads_dir}"
        )

    def modified_time(path: Path) -> float:
        return path.stat().st_mtime

    return str(max(matching_files, key=modified_time))


def normalize_name(name: str) -> str:
    """Normalize names across platforms by stripping trailing spaces,

    handling known nicknames, stripping generational suffixes, and punctuation.
    """
    if not isinstance(name, str):
        return ''
    cleaned = name.strip()
    cleaned = NAME_ALIASES.get(cleaned, cleaned)
    cleaned = re.sub(r'\b(Jr\.?|Sr\.?|II|III|IV)\b', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[.']", '', cleaned)
    return ' '.join(cleaned.split()).lower()


def match_dfs_players(
    dk_file: str | None = None,
    salaries_file: str = 'player_salaries.csv',
    output_file: str = 'matched_player_projections.csv',
) -> None:
    if dk_file is None:
        dk_file = newest_dk_file()

    dk_df = pd.read_csv(dk_file)
    sal_df = pd.read_csv(salaries_file)

    # Generate normalized keys for matching
    dk_df['join_key'] = dk_df['Player'].apply(normalize_name)
    sal_df['join_key'] = sal_df['Name'].apply(normalize_name)

    # Rename salary column from player_salaries to avoid name collision
    sal_df = sal_df.rename(columns={'Salary': 'Extracted Salary'})

    unmatched_df = dk_df[~dk_df['join_key'].isin(sal_df['join_key'])].drop(columns=['join_key'])
    print(f'Unmatched players: {len(unmatched_df)}')
    for _, player in unmatched_df.iterrows():
        print(f'{player["Player"]} ({player["DK Pos"]}, {player["Team"]}): DK Salary={player["DK Salary"]}')
    print()

    # Merge projection data with the extracted salaries
    merged_df = pd.merge(
        dk_df,
        sal_df[['join_key', 'Extracted Salary']],
        on='join_key',
        how='inner',
    ).drop(columns=['join_key'])
    merged_df = merged_df.drop(
        columns=['Small Field', 'Large Field', 'DK Floor', 'DK Ceiling', 'id'],
        errors='ignore',
    )

    # Clean up any trailing whitespace in display names (e.g. defense names like 'Chargers ')
    merged_df['Player'] = merged_df['Player'].str.strip()
    dk_salary = pd.to_numeric(
        merged_df['DK Salary'].astype('string').str.replace(r'[$,]', '', regex=True),
        errors='coerce',
    )
    extracted_salary = pd.to_numeric(
        merged_df['Extracted Salary'].astype('string').str.replace(r'[$,]', '', regex=True),
        errors='coerce',
    )
    dk_value = pd.to_numeric(merged_df['DK Value'], errors='coerce')
    merged_df['Extracted Value'] = [
        calculate_extracted_value(value, dk_sal, extracted_sal, position)
        for value, dk_sal, extracted_sal, position in zip(
            dk_value, dk_salary, extracted_salary, merged_df['DK Pos'], strict=True
        )
    ]

    players_to_display = merged_df[
        (merged_df['Extracted Value'] >= dk_value) & (merged_df['Extracted Value'] > -1)
    ].assign(**{'DK Value Numeric': dk_value})

    # Place both salary columns side-by-side
    cols = merged_df.columns.tolist()
    dk_idx = cols.index('DK Salary')
    cols.insert(dk_idx + 1, cols.pop(cols.index('Extracted Salary')))
    cols.insert(dk_idx + 2, cols.pop(cols.index('Extracted Value')))
    merged_df = merged_df[cols]

    merged_df.to_csv(output_file, index=False)
    print(f"Successfully matched {len(merged_df)} players -> '{output_file}'")
    print('Players with higher or unchanged Extracted Value by position:')
    for position in ('QB', 'RB', 'WR', 'TE', 'DST'):
        position_players = players_to_display[players_to_display['DK Pos'] == position].sort_values(
            'Extracted Value', ascending=False
        )
        if position_players.empty:
            continue
        print(position)
        print('Player, DK Value, Extracted Value, Difference')
        for _, player in position_players.iterrows():
            difference = round(player['Extracted Value'] - player['DK Value Numeric'], 1)
            print(f'{player["Player"]}, {player["DK Value Numeric"]}, {player["Extracted Value"]}, {difference}')
        print()


if __name__ == '__main__':
    export_player_salaries_to_csv(newest_season_dfs_file(), 'player_salaries.csv')
    match_dfs_players()
