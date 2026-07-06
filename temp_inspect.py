import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 데이터 로드
df = pd.read_csv('yes24/data/yes24_bestseller.csv', encoding='utf-8')

# 기본 정보
print("SHAPE:", df.shape)
print("COLUMNS:", df.columns.tolist())
print("\n--- INFO ---")
df.info()
print("\n--- NULL VALUES ---")
print(df.isnull().sum())
print("\n--- DUPLICATED ROWS ---")
print(df.duplicated().sum())

print("\n--- DESCRIBE NUMERIC ---")
print(df.describe())

print("\n--- DESCRIBE CATEGORICAL ---")
print(df.describe(include=['object']))

print("\n--- HEAD 5 ---")
print(df.head(5))
print("\n--- TAIL 5 ---")
print(df.tail(5))
