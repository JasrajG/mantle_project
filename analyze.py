import pandas as pd
import numpy as np

# 1. Load the Tab 2 Reference Data
valid_funds_df = pd.read_csv("fund_investment_map.csv")
valid_clients_df = pd.read_csv("clients_list.csv")
fee_rates_df = pd.read_csv("fee_rates.csv")
return_rates_df = pd.read_csv("return_rates.csv")

# Create fast-lookup dictionaries and sets for validation
# Convert everything to lowercase for safe comparisons
valid_clients = set(valid_clients_df.iloc[:, 0].str.strip().str.lower())
valid_fund_investments = set(zip(
    valid_funds_df.iloc[:, 0].str.strip().str.lower(),
    valid_funds_df.iloc[:, 1].str.strip().str.lower()
))
expected_fees = dict(zip(
    fee_rates_df.iloc[:, 0].str.strip().str.lower(), 
    fee_rates_df.iloc[:, 1].astype(float)
))
expected_rors = dict(zip(
    return_rates_df.iloc[:, 0].str.strip().str.lower(), 
    return_rates_df.iloc[:, 1].astype(float)
))

# 2. Load and Merge Ledgers (Tabs 3 & 4)
df_tab3 = pd.read_csv("performance_report.csv")
df_tab4 = pd.read_csv("annual_summary.csv")

df_tab3.columns = df_tab3.columns.str.strip().str.lower()
df_tab4.columns = df_tab4.columns.str.strip().str.lower()

rename_map = {
    'statement date': 'Date', 'statement_date': 'Date',
    'name': 'Client', 'client_name': 'Client',
    'fund ': 'Fund', 'fund': 'Fund', 'fund_name': 'Fund',
    'investment': 'Investment', 'investment_name': 'Investment',
    'starting amount': 'Starting Balance', 'starting_balance': 'Starting Balance',
    'ending amount': 'Reported Ending Balance', 'ending_balance': 'Reported Ending Balance',
    'profit': 'Profit', 'fee': 'Fee'
}
df_tab3 = df_tab3.rename(columns=rename_map)
df_tab4 = df_tab4.rename(columns=rename_map)

# Add fallback Date if Tab 4 is missing one
if 'Date' not in df_tab4.columns: df_tab4['Date'] = "Dec 31, 2024"

# Clean currency ($ and commas) to float
def clean_money(c): return c.astype(str).str.replace(r'[\$,]', '', regex=True).astype(float)
for col in ["Starting Balance", "Reported Ending Balance", "Profit", "Fee"]:
    if col in df_tab3.columns: df_tab3[col] = clean_money(df_tab3[col])
    if col in df_tab4.columns: df_tab4[col] = clean_money(df_tab4[col])

cols = ["Date", "Client", "Fund", "Investment", "Starting Balance", "Profit", "Fee", "Reported Ending Balance"]
df = pd.concat([df_tab3[cols], df_tab4[cols]], ignore_index=True)

# Standardize company strings
df['Fund'] = df['Fund'].astype(str).str.strip().replace({
    'moonstripe': 'Moonstripe', 
    'west grove banking': 'West Grove Banking Inc.', 
    'West Grove Banking': 'West Grove Banking Inc.', 
    'belladonna': 'Belladonna',
    'Belladonna Investing': 'Belladonna'
})
df['Investment'] = df['Investment'].astype(str).str.strip().replace({'breakbank series iv': 'Breakbank Series IV', 'breakbank series vi': 'Breakbank Series VI', 'calrose group fund 3': 'Calrose Group Fund III', 'calrose group fund iii': 'Calrose Group Fund III', 'lemur ventures': 'Lemur Ventures LLC'})

# 3. Math & Logic Validations
df['Calculated Ending Balance'] = df['Starting Balance'] + df['Profit'] - df['Fee']
df['Calculated RoR'] = df['Profit'] / df['Starting Balance']
df['Calculated Fee'] = df['Fee'] / df['Profit']

def validate_row(row):
    notes = []
    # 1. Math Check
    diff = abs(row['Reported Ending Balance'] - row['Calculated Ending Balance'])
    if diff > 0.05:
        notes.append(f"Math Typo: Reported ${row['Reported Ending Balance']:,.2f} but math requires ${row['Calculated Ending Balance']:,.2f}.")
    
    # 2. Unknown Client Check
    if row['Client'].lower() not in valid_clients:
        notes.append("Logic Error: Client is not on the authorized list.")
        
    # 3. Invalid Fund/Investment Mapping Check
    fund_inv_combo = (row['Fund'].lower(), row['Investment'].lower())
    if fund_inv_combo not in valid_fund_investments:
        notes.append(f"Logic Error: {row['Fund']} does not manage {row['Investment']}.")
        
    # 4. Rate of Return Check
    exp_ror = expected_rors.get(row['Investment'].lower())
    if exp_ror is not None and abs(row['Calculated RoR'] - exp_ror) > 0.005:
        notes.append(f"Rate Error: Charged RoR {row['Calculated RoR']:.1%} (Expected {exp_ror:.1%}).")
        
    # 5. Fee Rate Check
    exp_fee = expected_fees.get(row['Fund'].lower())
    if exp_fee is not None and abs(row['Calculated Fee'] - exp_fee) > 0.005:
        notes.append(f"Fee Error: Charged Fee {row['Calculated Fee']:.1%} (Expected {exp_fee:.1%}).")

    return " | ".join(notes) if notes else "Valid"

df['Correction Note'] = df.apply(validate_row, axis=1)
df['Error Flag'] = df['Correction Note'] != "Valid"

# 4. Final Output Formatting
final_cols = ["Date", "Client", "Fund", "Investment", "Starting Balance", "Profit", "Fee", "Reported Ending Balance", "Calculated Ending Balance", "Error Flag", "Correction Note"]
df_final = df[final_cols]
df_final.to_csv("Final_Validated_Ledger.csv", index=False)

print("\n✅ Successfully generated Final_Validated_Ledger.csv!")
print("Here is a summary of the data integrity issues found:")
print(df_final[df_final['Error Flag']][['Client', 'Correction Note']])

print("\n" + "="*50)
print(" AUTOMATED ANSWERS TO ASSESSMENT QUESTIONS")
print("="*50)

# 1. Which fund charges the highest fees?
# Locate the max fee rate in the Tab 2 reference table
highest_fee_idx = fee_rates_df.iloc[:, 1].astype(float).idxmax()
highest_fee_fund = fee_rates_df.iloc[highest_fee_idx, 0].strip()
highest_fee_rate = float(fee_rates_df.iloc[highest_fee_idx, 1])
print(f"1. Which fund charges the highest fees?")
print(f"   -> {highest_fee_fund} at {highest_fee_rate:.1%}\n")

# 2. Which investments had the best rate of returns? What is the rate?
highest_ror_idx = return_rates_df.iloc[:, 1].astype(float).idxmax()
highest_ror_inv = return_rates_df.iloc[highest_ror_idx, 0].strip()
highest_ror_rate = float(return_rates_df.iloc[highest_ror_idx, 1])
print(f"2. Which investments had the best rate of returns? What is the rate?")
print(f"   -> {highest_ror_inv} at {highest_ror_rate:.1%}\n")

# 3. Which client had the highest profit (in absolute $) in this period?
# Group by client and sum the profits
client_profits = df_final.groupby('Client')['Profit'].sum()
best_client = client_profits.idxmax()
best_client_profit = client_profits.max()
print(f"3. Which client had the highest profit?")
print(f"   -> {best_client} with a total profit of ${best_client_profit:,.2f}\n")

# 4. How much profit in total did Alfred Bank earn before fees?
alfred_profit = client_profits.get("Alfred Banks", 0) # Exact name from valid list
print(f"4. How much profit in total did Alfred Banks earn before fees?")
print(f"   -> ${alfred_profit:,.2f}\n")

# 5. Were there any typos or errors in the data?
print(f"5. Were there any typos or errors in the data?")
print(f"   -> Yes, several data integrity issues were found:")
error_rows = df_final[df_final['Error Flag']]
for _, row in error_rows.iterrows():
    print(f"      - {row['Client']} ({row['Investment']}): {row['Correction Note']}")
print()

# 6. What is the end balance of Cathy Danvers fund?
cathy_data = df_final[df_final['Client'].str.contains('Cathy Danvers', case=False, na=False)].iloc[0]
print(f"6. What is the end balance of Cathy Danvers' fund?")
print(f"   -> The reported ending balance was ${cathy_data['Reported Ending Balance']:,.2f}, however, based on the formula (Start + Profit - Fee), the mathematically correct ending balance is ${cathy_data['Calculated Ending Balance']:,.2f}.")
print("="*50 + "\n")