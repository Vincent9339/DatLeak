import pandas as pd
import numpy as np
import sys, ast

def detect_row_leakage(df_original, df_scrambled, ignore_value=None, ignore_col=None):
    try:
        if df_original.shape != df_scrambled.shape:
            print(" - Error: DataFrames do not have the same shape.")
            return None

        if ignore_col is not None:
            try:
                if isinstance(ignore_col, int):
                    ignore_col = [ignore_col]
                elif isinstance(ignore_col, str):
                    try:
                        ignore_col = ast.literal_eval(ignore_col)
                        if isinstance(ignore_col, int):
                            ignore_col = [ignore_col]
                    except (ValueError, SyntaxError):
                        ignore_col = [int(col.strip()) for col in ignore_col.split(',') if col.strip().isdigit()]               
                ignore_col = [col for col in ignore_col if isinstance(col, int) and 0 <= col < len(df_original.columns)]
                
                if ignore_col:
                    df_original = df_original.drop(df_original.columns[ignore_col], axis=1)
                    df_scrambled = df_scrambled.drop(df_scrambled.columns[ignore_col], axis=1)
            except Exception as e:
                print(f" - Error processing ignore_col parameter: {str(e)}")
                print(f" - Please insert a value for a column, or leave it empty.")                
                return None

        total_rows = df_original.shape[0]
        partial_leakage_count = 0
        full_leakage_count = 0
        matching_cells_per_row = []

        for idx, (row_orig, row_scram) in enumerate(zip(df_original.iterrows(), df_scrambled.iterrows())):
            try:
                row_orig = row_orig[1]
                row_scram = row_scram[1]
                
                try:
                    if ignore_value is not None:
                        valid_mask = (row_orig != ignore_value) & (row_scram != ignore_value)
                    else:
                        valid_mask = pd.Series(True, index=row_orig.index)
                except Exception as e:
                    print(f" - Error creating valid mask for row {idx}: {str(e)}")
                    continue
                try:
                    matches = (row_orig[valid_mask] == row_scram[valid_mask])
                    match_count = matches.sum()
                    matching_cells_per_row.append(match_count)
                except Exception as e:
                    print(f" - Error comparing rows at index {idx}: {str(e)}")
                    continue
                try:
                    valid_count = valid_mask.sum()
                    if match_count == valid_count:
                        full_leakage_count += 1
                    elif 0 < match_count < valid_count:
                        partial_leakage_count += 1
                except Exception as e:
                    print(f" - Error counting matches for row {idx}: {str(e)}")
                    continue
            except Exception as e:
                print(f" - Error processing row {idx}: {str(e)}")
                continue
        try:
            partial_leakage_percentage = (partial_leakage_count / total_rows) * 100 if total_rows > 0 else 0
            full_leakage_percentage = (full_leakage_count / total_rows) * 100 if total_rows > 0 else 0
            avg_matching_cells_per_row = np.mean(matching_cells_per_row) if total_rows > 0 else 0
            std_matching_cells_per_row = np.std(matching_cells_per_row) if total_rows > 0 else 0
        except Exception as e:
            print(f" - Error calculating final metrics: {str(e)}")
            return None
            
        if full_leakage_percentage > 0:
            print(f" - NOTICE: Privacy is not preserved. Please consider re-scramble/re-noise your data.\n") 
        return partial_leakage_percentage, full_leakage_percentage, avg_matching_cells_per_row, std_matching_cells_per_row

    except Exception as e:
        print(f" - Unexpected error in detect_row_leakage: {str(e)}")
        return None

if __name__ == "__main__":
    try:
        if len(sys.argv) < 3:
            print(" - Usage: python DatLeak.py <original_file> <scrambled_file> [ignore_value] [ignore_col]")
            sys.exit(1)

        try:
            original_file = sys.argv[1]
            scrambled_file = sys.argv[2]
            ignore_value = sys.argv[3] if len(sys.argv) > 3 else None
            ignore_col = sys.argv[4] if len(sys.argv) > 4 else None
        except IndexError:
            print(" - Error: Missing required arguments")
            print(" - Usage: python DatLeak.py <original_file> <scrambled_file> [ignore_value] [ignore_col]")
            print(" - This run will be terminated.")
            sys.exit(1)

        try:
            original_df = pd.read_csv(original_file, delimiter='\t' if original_file.endswith('.tsv') else ',')
            scrambled_df = pd.read_csv(scrambled_file, delimiter='\t' if scrambled_file.endswith('.tsv') else ',')
        except Exception as e:
            print(f" - Error loading files: {str(e)}")
            sys.exit(1)

        metrics = detect_row_leakage(original_df, scrambled_df, ignore_value, ignore_col)
        if metrics:
            partial_leakage, full_leakage, avg_match, std_match = metrics
            print(f" - Full Leakage (identical row/participant): {full_leakage:.2f}%")
            print(f" - Partial Leakage (rows/participants have data partially identical): {partial_leakage:.2f}%")
            print(f" - Average portion of row/participants that are identical: {avg_match:.2f}")
            print(f" - Standard Deviationof row/participants that are identical: {std_match:.2f}")
        else:
            print(" - Error: Could not calculate leakage metrics")
            sys.exit(1)

    except Exception as e:
        print(f"- Unexpected error in main execution: {str(e)}")
        sys.exit(1)
