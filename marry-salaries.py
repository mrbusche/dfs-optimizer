import csv
import re
from pathlib import Path

import pandas as pd

NAME_ALIASES = {
    'Nick Singleton': 'Nicholas Singleton',
    'Matt Hibner': 'Matthew Hibner',
}

DK_FILE_PREFIX = 'DraftKings NFL DFS Projections -- Main Slate'
VALUE_PER_THOUSAND = {'QB': 3, 'RB': 2, 'WR': 2, 'TE': 2, 'DST': 2}


def calculate_extracted_value(dk_value: float, dk_salary: float, extracted_salary: float, position: str) -> float:
    try:
        value_per_thousand = VALUE_PER_THOUSAND[position]
    except KeyError:
        raise ValueError(f'Unsupported DraftKings position: {position}') from None

    return round(dk_value + (dk_salary - extracted_salary) * value_per_thousand / 1000, 1)


def export_player_salaries_to_csv(
    input_file: str,
    output_file: str = 'player_salaries.csv',
) -> None:
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    pattern = re.compile(
        r'^(?:RB|WR|QB|TE|DST)\s*\n+^([^\n]+?)\s*\n+(?:.*?\n+)*?^\$([0-9,]+)',
        re.MULTILINE,
    )

    records = []
    for match in pattern.finditer(text):
        name = match.group(1).strip()
        salary = int(match.group(2).replace(',', ''))
        records.append((name, salary))

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
    return str(max(matching_files, key=lambda path: path.stat().st_mtime))


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

    qualifying_players = (
        merged_df[(merged_df['Extracted Value'] > dk_value) & (merged_df['Extracted Value'] > 1)]
        .assign(**{'DK Value Numeric': dk_value})
        .sort_values('Extracted Value', ascending=False)
    )

    # Place both salary columns side-by-side
    cols = merged_df.columns.tolist()
    dk_idx = cols.index('DK Salary')
    cols.insert(dk_idx + 1, cols.pop(cols.index('Extracted Salary')))
    cols.insert(dk_idx + 2, cols.pop(cols.index('Extracted Value')))
    merged_df = merged_df[cols]

    merged_df.to_csv(output_file, index=False)
    print(f"Successfully matched {len(merged_df)} players -> '{output_file}'")
    print('Players with higher Extracted Value:')
    for _, player in qualifying_players.iterrows():
        print(f'{player["Player"]}: Extracted Value={player["Extracted Value"]}, DK Value={player["DK Value Numeric"]}')


if __name__ == '__main__':
    export_player_salaries_to_csv('Season DFS.txt', 'player_salaries.csv')
    match_dfs_players()
