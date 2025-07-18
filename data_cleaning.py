import pandas as pd

# 1. Load the uncleaned Excel file
file_path = "uncleaned.xlsx"  # Make sure the file is in your PyCharm project folder
df = pd.read_excel(file_path)

# 2. Remove duplicate rows (optional)
df = df.drop_duplicates()

# 3. Clean 'Full Name'
df['Full Name'] = df['Full Name'].astype(str).str.strip()
df = df[df['Full Name'].notna() & (df['Full Name'] != 'nan')]

# 4. Clean 'Salary'
df['Salary'] = df['Salary'].astype(str).str.replace('₹', '', regex=False).str.replace(',', '', regex=False)
df['Salary'] = pd.to_numeric(df['Salary'], errors='coerce')
df = df[df['Salary'].notna()]

# 5. Clean 'Gender'
df['Gender'] = df['Gender'].astype(str).str.strip().str.lower()
df = df[df['Gender'].isin(['male', 'female'])]

# 6. Clean 'Age'
df = df[df['Age'] <= 120]

# 7. Clean 'Remarks'
df['Remarks'] = df['Remarks'].astype(str) \
    .str.replace('\n', '', regex=False) \
    .str.replace('\t', '', regex=False) \
    .str.strip()
df = df[df['Remarks'] != 'nan']

# 8. Clean 'DOJ' (Date of Joining)
df['DOJ'] = pd.to_datetime(df['DOJ'], errors='coerce')
df = df[df['DOJ'].notna()]

# 9. Reset index
df = df.reset_index(drop=True)

# 10. Save cleaned data to a new file
cleaned_file_path = "cleaned_uncleaned.xlsx"
df.to_excel(cleaned_file_path, index=False)

print(f"✅ Cleaning done! Cleaned file saved as: {cleaned_file_path}")
