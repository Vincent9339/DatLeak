import pandas as pd
import numpy as np
import sys

def detect_row_leakage(df_original, df_scrambled, ignore_value=None):
    if df_original.shape != df_scrambled.shape:
        print("DataFrames do not have the same shape.")
        return

    total_rows = df_original.shape[0]
    total_columns = df_original.shape[1]
    partial_leakage_count = 0
    full_leakage_count = 0
    matching_cells_per_row = []

    for idx, (row_orig, row_scram) in enumerate(zip(df_original.iterrows(), df_scrambled.iterrows())):
        row_orig = row_orig[1]
        row_scram = row_scram[1]
        valid_mask = (row_orig != ignore_value) & (row_scram != ignore_value) if ignore_value is not None else True

        matches = (row_orig[valid_mask] == row_scram[valid_mask])
        match_count = matches.sum()
        matching_cells_per_row.append(match_count)

        # Check for full leakage
        if match_count == valid_mask.sum():
            full_leakage_count += 1
        # Check for partial leakage
        elif 0 < match_count < valid_mask.sum():
            partial_leakage_count += 1

    partial_leakage_percentage = (partial_leakage_count / total_rows) * 100 if total_rows > 0 else 0
    full_leakage_percentage = (full_leakage_count / total_rows) * 100 if total_rows > 0 else 0

    avg_matching_cells_per_row = np.mean(matching_cells_per_row) if total_rows > 0 else 0
    std_matching_cells_per_row = np.std(matching_cells_per_row) if total_rows > 0 else 0

    return partial_leakage_percentage, full_leakage_percentage, avg_matching_cells_per_row, std_matching_cells_per_row

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python DatLeak.py <original_file> <scrambled_file> [ignore_value]")
        sys.exit(1)

    original_file = sys.argv[1]
    scrambled_file = sys.argv[2]
    ignore_value = sys.argv[3] if len(sys.argv) > 3 else None

    # Detect file type (CSV or TSV) and load
    original_df = pd.read_csv(original_file, delimiter='\t' if original_file.endswith('.tsv') else ',')
    scrambled_df = pd.read_csv(scrambled_file, delimiter='\t' if scrambled_file.endswith('.tsv') else ',')

    # Run leakage detection
    metrics = detect_row_leakage(original_df, scrambled_df, ignore_value)
    if metrics:
        partial_leakage, full_leakage, avg_match, std_match = metrics
        print(f"Partial Leakage: {partial_leakage:.2f}%")
        print(f"Full Leakage: {full_leakage:.2f}%")
        print(f"Average Matching Cells per Row: {avg_match:.2f}")
        print(f"Standard Deviation of Matching Cells per Row: {std_match:.2f}")
