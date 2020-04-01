
import pandas as pd
df = pd.read_excel("Classes.xlsx")
print(df)

print(df.columns)
print("Enrollment" in df.columns)
