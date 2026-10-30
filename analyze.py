import pandas as pd

# 1. Load the extracted tables from main.py
df_tab3 = pd.read_csv("performance_report_2024.csv")
df_tab4 = pd.read_csv("investments_annual_summary.csv")

# 2. Standardize Column Names so we can stack them safely
df_tab3 = df_tab3.rename(columns={
    "Name": "Client",
    "Fund ": "Fund",
    "Fund": "Fund",
    "Investment": "Investment",
    "Starting Amount": "Starting Balance",
    "Ending Amount": "Ending Balance",
    "profit": "Profit",
    "fee": "Fee"
})

df_tab4 = df_tab4.rename(columns={
    "client_name": "Client",
    "fund_name": "Fund",
    "investment_name": "Investment",
    "starting_balance": "Starting Balance",
    "ending_balance": "Ending Balance",
    "profit": "Profit",
    "fee": "Fee"
})

# Keep only the essential financial columns to merge
cols = ["Client", "Fund", "Investment", "Starting Balance", "Ending Balance", "Profit", "Fee"]
df_merged = pd.concat([df_tab3[cols], df_tab4[cols]], ignore_index=True)

# 3. Clean and Standardize Text Data (Handle differing manual entry cases)
def clean_names(text):
    if pd.isna(text): return text
    return str(text).strip().lower()

df_merged['Fund'] = df_merged['Fund'].apply(clean_names).replace({
    'moonstripe': 'Moonstripe',
    'west grove banking': 'West Grove Banking Inc.',
    'west grove banking inc.': 'West Grove Banking Inc.',
    'belladonna': 'Belladonna Investing',
    'belladonna investing': 'Belladonna Investing'
})

df_merged['Investment'] = df_merged['Investment'].apply(clean_names).replace({
    'breakbank series iv': 'Breakbank Series IV',
    'breakbank series vi': 'Breakbank Series VI',
    'calrose group fund 3': 'Calrose Group Fund 3',
    'calrose group fund iii': 'Calrose Group Fund 3',
    'lemur ventures': 'Lemur Ventures LLC',
    'lemur ventures llc': 'Lemur Ventures LLC'
})

# 4. Math Validations (Find the Typos)
# Formula: [End Balance] = [Starting Balance] + [Profit] - [Fees]
df_merged['Calculated End Balance'] = df_merged['Starting Balance'] + df_merged['Profit'] - df_merged['Fee']

# Flag Typos (Allowing a 5-cent buffer for standard rounding differences)
df_merged['Data Entry Error Flag'] = abs(df_merged['Ending Balance'] - df_merged['Calculated End Balance']) > 0.05

# 5. Output answers to console for the questions
print("=== Question 1: Highest Fee Fund ===")
# Fees = Profit * Fee_rate -> Fee_rate = Fees / Profit
df_merged['Calculated Fee Rate'] = df_merged['Fee'] / df_merged['Profit']
highest_fee = df_merged.groupby('Fund')['Calculated Fee Rate'].mean().idxmax()
print(f"Highest fee fund: {highest_fee}\n")

print("=== Question 2: Best Rate of Return ===")
# Profit = Rate_of_return * Starting Balance -> Rate = Profit / Starting
df_merged['Calculated Rate of Return'] = df_merged['Profit'] / df_merged['Starting Balance']
best_return = df_merged.groupby('Investment')['Calculated Rate of Return'].mean().idxmax()
best_rate = df_merged.groupby('Investment')['Calculated Rate of Return'].mean().max()
print(f"Best return investment: {best_return} ({best_rate:.2%})\n")

print("=== Question 3: Client with Highest Profit ===")
profit_by_client = df_merged.groupby('Client')['Profit'].sum()
top_client = profit_by_client.idxmax()
print(f"{top_client} earned ${profit_by_client.max():,.2f}\n")

print("=== Question 4: Alfred Banks Profit ===")
print(f"Alfred Banks Total Profit: ${profit_by_client.get('Alfred Banks', 0):,.2f}\n")

print("=== Question 5 & 6: Errors & Cathy Danvers ===")
errors = df_merged[df_merged['Data Entry Error Flag']]
print(f"Found {len(errors)} major errors in End Balances:")
for _, row in errors.iterrows():
    print(f"- {row['Client']}: Typed as ${row['Ending Balance']:,.2f}, should be ${row['Calculated End Balance']:,.2f}")
print()

# 6. Save the final merged & corrected sheet
output_file = "Jasraj_Gill_PerformanceReport2024.csv"
df_merged.to_csv(output_file, index=False)
print(f"Successfully exported final clean data to: {output_file}")