import pandas as pd

#link provided (side note: I would not do this for a real job, I would either have the data on a local machine or have it behind a secure system and store my credentials on a local enviornment file)
pub_id = "2PACX-1vTveSdJZ-yzmCRqDF1EpdtNdMVfBKm1sWNQFOvVSo86jLl6DUe7IbWYREWjJg9MZQ_iFD0XalKecDXs"
file_source = f"https://docs.google.com/spreadsheets/d/e/{pub_id}/pub?output=xlsx"

print("Downloading live data from Google Sheets...")
all_sheets = pd.read_excel(file_source, sheet_name=None, header=None)

def sheet_contains(df, keyword):
    return df.apply(lambda col: col.astype(str).str.contains(keyword, case=False, na=False)).any().any()

rules_sheet, perf_sheet, annual_sheet = None, None, None

print("Scanning tabs for actual data (ignoring hidden/copy sheets)...")
for name, df in all_sheets.items():
    # DEFENSIVE FILTER: Ignore hidden scratchpads or backup copies (these are the hidden sheets)
    if "copy of" in name.lower() or "reference" in name.lower():
        print(f" -> Skipping hidden/backup sheet: '{name}'")
        continue

    # Identify the real sheets based on their contents
    if sheet_contains(df, "This is the list of funds") and rules_sheet is None:
        rules_sheet = df
        print(f" -> Found Official Rules tab: '{name}'")
    elif sheet_contains(df, "Statement Date") and sheet_contains(df, "Starting Amount") and perf_sheet is None:
        perf_sheet = df
        print(f" -> Found Official Performance Report tab: '{name}'")
    elif sheet_contains(df, "account_id") and annual_sheet is None:
        annual_sheet = df
        print(f" -> Found Official Annual Summary tab: '{name}'")

# --- Extract Tab 2 Reference Tables ---
def parse_tab2_with_descriptions(df):
    tables, current_desc, current_headers, current_rows = {}, "", None, []
    for _, row in df.iterrows():
        if row.dropna().empty:
            if current_desc and current_headers and current_rows:
                tables[current_desc] = pd.DataFrame(current_rows, columns=current_headers)
                current_desc, current_headers, current_rows = "", None, []
            continue
        
        val0 = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        
        if val0.startswith("This is"):
            current_desc = val0
            current_headers, current_rows = None, []
            continue
        if current_desc and current_headers is None:
            current_headers = row.dropna().tolist()
            continue
        if current_desc and current_headers:
            current_rows.append(row.iloc[:len(current_headers)].values)

    if current_desc and current_headers and current_rows:
        tables[current_desc] = pd.DataFrame(current_rows, columns=current_headers)
    return tables

print("\nExtracting Rules...")
tab2_tables = parse_tab2_with_descriptions(rules_sheet)
table_files = ["fund_investment_map.csv", "clients_list.csv", "fee_rates.csv", "return_rates.csv"]
for idx, (desc, tbl) in enumerate(tab2_tables.items()):
    tbl.to_csv(table_files[idx], index=False)

# --- Extract Ledgers ---
def parse_table_by_header(df, keyword):
    for idx, row in df.iterrows():
        if any(keyword.lower() in str(v).strip().lower() for v in row.values if pd.notna(v)):
            clean_df = df.iloc[idx + 1:].copy()
            clean_df.columns = row.values
            return clean_df.dropna(how="all").dropna(how="all", axis=1).reset_index(drop=True)
    return df

print("Extracting Ledgers...")
df_tab3 = parse_table_by_header(perf_sheet, "Statement Date")
df_tab3.to_csv("performance_report.csv", index=False)

df_tab4 = parse_table_by_header(annual_sheet, "account_id")
df_tab4.to_csv("annual_summary.csv", index=False)

print("\n✅ Extraction Complete! Run analyze.py next.")