import pandas as pd

print('111111')
file_path = r"D:\python\beauty-bot\beauty_products.xlsx"

try:
    excel_file = pd.ExcelFile(file_path, engine="openpyxl")
    print("📄 Sheet names:", excel_file.sheet_names)

except Exception as e:
    print("❌ Error loading file1:", e)


df = pd.read_excel(excel_file, sheet_name=excel_file.sheet_names[0])
print(f"\n✅ Loaded: {df.shape[0]} rows × {df.shape[1]} columns")

print("\n📦 Columns:")
print(df.columns.tolist())
print(df.head())
# Show first 5 rows
print("\n🔍 Preview:")
print(df.head())
