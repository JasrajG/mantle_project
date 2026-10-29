import pandas as pd

# Load workbook (works with live url or local .xlsx file)
pub_id = "2PACX-1vTUgf6BrYd1a8tSj1eh17HRPcl-NRgZNUF4SZnLo_Ic2N9x5hABCybmlgfoGAtOrL5uSYlWpD0Wn6Xd"
file_source = f"https://docs.google.com/spreadsheets/d/e/{pub_id}/pub?output=xlsx"
# Note: If reading locally, change file_source to 'Copy of Interview Question for Data Operations.xlsx'

all_sheets = pd.read_excel(file_source, sheet_name=None, header=None)
sheet_names = list(all_sheets.keys())

# --- TAB 1: Skipped ---
print(f"Skipping Tab 1: '{sheet_names[0]}'\n")


# --- TAB 2: Split multi-table sheet with descriptions ---
def parse_tab2_with_descriptions(df):
    tables = {}
    current_desc = ""
    current_headers = None
    current_rows = []

    for idx, row in df.iterrows():
        # Empty row marks end of a table
        if row.dropna().empty:
            if current_desc and current_headers and current_rows:
                tables[current_desc] = pd.DataFrame(current_rows, columns=current_headers)
                current_desc, current_headers, current_rows = "", None, []
            continue

        val0 = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""

        # Identify description row
        if val0.startswith("This is"):
            current_desc = val0
            current_headers, current_rows = None, []
            continue

        # Identify table header row
        if current_desc and current_headers is None:
            current_headers = row.dropna().tolist()
            continue

        # Accumulate table data rows
        if current_desc and current_headers:
            current_rows.append(row.iloc[: len(current_headers)].values)

    # Catch final table block
    if current_desc and current_headers and current_rows:
        tables[current_desc] = pd.DataFrame(current_rows, columns=current_headers)

    return tables


tab2_tables = parse_tab2_with_descriptions(all_sheets[sheet_names[1]])

# Save Tab 2 tables individually
print("--- Tab 2 Extracted Tables ---")
for idx, (desc, tbl) in enumerate(tab2_tables.items(), start=1):
    filename = f"tab2_table{idx}.csv"
    tbl.to_csv(filename, index=False)
    print(f"[{filename}] {desc}")


# --- TABS 3 & 4: Single tables with variable header rows ---
def parse_table_by_header(df, target_header_keyword):
    for idx, row in df.iterrows():
        row_str = [str(v).strip().lower() for v in row.values if pd.notna(v)]
        if any(target_header_keyword.lower() in v for v in row_str):
            clean_df = df.iloc[idx + 1 :].copy()
            clean_df.columns = row.values
            return clean_df.dropna(how="all").dropna(how="all", axis=1).reset_index(drop=True)
    return df


# Tab 3 (PerformanceReport2024)
df_tab3 = parse_table_by_header(all_sheets[sheet_names[2]], "Statement Date")
df_tab3.to_csv("performance_report_2024.csv", index=False)
print(f"\n--- Saved Tab 3 -> performance_report_2024.csv ({len(df_tab3)} rows) ---")

# Tab 4 (investments-annual-summary)
# Dynamically target index based on tab count
tab4_index = 3 if len(sheet_names) <= 4 else 4
df_tab4 = parse_table_by_header(all_sheets[sheet_names[tab4_index]], "account_id")
df_tab4.to_csv("investments_annual_summary.csv", index=False)
print(f"--- Saved Tab 4 -> investments_annual_summary.csv ({len(df_tab4)} rows) ---")