# Data Cleaning - Student's Grade
import pandas as pd
import numpy as np
import os

# -----------------------------
# 1. Load Data
# -----------------------------

# Get script folder
script_dir = os.path.dirname(os.path.abspath(__file__))

# Build correct path
file_path = os.path.join(script_dir, "..", "data", "student_scores_raw.csv")

# Normalize path
file_path = os.path.abspath(file_path)

print("Looking for file at:")
print(file_path)

# Load dataset
data = pd.read_csv(file_path)

print("Dataset loaded successfully")
print(data.head())

# -----------------------------
# 2. Standardize Column Names
# -----------------------------

data.columns = data.columns.str.strip().str.lower()

print("\nColumns:")
print(data.columns)


# -----------------------------
# 3. Data Quality Check
# -----------------------------

def data_quality_check(df):
    report = {
        "Missing Values": df.isnull().sum(),
        "Duplicate Rows": df.duplicated().sum(),
        "Data Types": df.dtypes,
        "Summary Statistics": df.describe(include='all')
    }
    return report

quality_report = data_quality_check(data)

print("\nData Quality Report:")
print(quality_report["Missing Values"])


# -----------------------------
# 4. Remove Duplicate Rows
# -----------------------------

initial_count = len(data)
df_clean = data.drop_duplicates(subset=['id'], keep='first')
print(f"\nRemoved {initial_count - len(df_clean)} duplicate rows")


# -----------------------------
# 5. Standardize Text Formats
# -----------------------------

df_clean["name"] = df_clean["name"].str.title()
df_clean["class_name"] = df_clean["class_name"].str.upper()
df_clean["grade"] = df_clean["grade"].str.upper()

# Convert numeric
df_clean["score"] = pd.to_numeric(df_clean["score"], errors="coerce")

# Convert date
df_clean["created_at"] = pd.to_datetime(df_clean["created_at"])
df_clean["updated_at"] = pd.to_datetime(df_clean["updated_at"])


# -----------------------------
# 6. Handle Missing Values
# -----------------------------

mean_score = df_clean["score"].mean()

df_clean["score"] = df_clean["score"].fillna(mean_score)
df_clean["grade"] = df_clean["grade"].fillna("Unknown")

print(f"\nFilled missing scores with mean: {round(mean_score,2)}")


# -----------------------------
# 7. Remove Invalid Scores
# -----------------------------

initial_count = len(df_clean)

df_clean = df_clean[df_clean["score"].between(0, 100)]

print(f"Removed {initial_count - len(df_clean)} invalid scores")


# -----------------------------
# 8. Assign Letter Grades
# -----------------------------

def assign_grade(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

df_clean["grade"] = df_clean["score"].apply(assign_grade)


# -----------------------------
# 9. Data Quality Flag
# -----------------------------

df_clean["score_flag"] = np.where(
    df_clean["score"].between(0, 100),
    "Valid",
    "Invalid"
)


# -----------------------------
# 10. Save Cleaned Data
# -----------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))

output_dir = os.path.join(script_dir, "..", "output")

os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, "student_scores_cleaned.csv")

df_clean.to_csv(output_path, index=False)

print("Cleaned file saved successfully:")
print(output_path)
