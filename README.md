# Mantle Data Assessment - Jasraj Gill

This repository contains the Python-based automated data pipeline I built to solve the Mantle Data Assessment. 

While the data could be merged manually, I chose to write a programmatic solution to ensure reproducibility, eliminate human error during the merge, and programmatically flag data integrity issues (like math typos, unauthorized clients, and invalid fund mappings).

## 🚀 How to Run the Code

**Prerequisites:** 
You will need Python 3 installed, along with the `pandas` and `openpyxl` libraries.
```bash
pip install pandas openpyxl
```
Step 1: Extract the Data
Run the extraction script. This script reaches out to the live Google Sheet, intelligently identifies the correct tabs (ignoring hidden/scratchpad sheets), and parses the data into clean, raw CSVs.


```bash
python extract.py
```

Step 2: Analyze and Validate
Run the analysis script. This script merges the ledgers, standardizes naming conventions, and performs mathematical and logical validations on every single row.


```bash
python analyze.py
```
This will generate Final_Validated_Ledger.csv and output the answers to the assessment questions directly in your terminal.

🧠 Methodology & Validation Logic
Because the prompt noted that much of the data was entered manually, I built a validate_row() function to perform strict QA on the dataset:

Math Checks: Calculated a theoretical ending balance (Start + Profit - Fee) and compared it to the reported ending balance. This successfully caught shifted-decimal typos for Alfred Banks and Cathy Danvers.

Client Authorization: Checked all ledger clients against the authorized Tab 2 list. This caught Kelvin Loggins and Marge Nestor as unauthorized clients.

Investment Mapping: Ensured the listed Fund actually manages the listed Investment. This flagged Gabriel Holland's row, as West Grove Banking does not manage Lemur Ventures.

Rate Verification: Calculated the actual fee and return rates applied in the ledgers and verified they perfectly matched the stated rates in the Tab 2 rules.

📊 Final Output
The final merged dataset, along with the automated error flags and answers to the assessment questions, can be found in the Google Sheets submission provided via email.