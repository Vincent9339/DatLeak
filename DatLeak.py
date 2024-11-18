detect_row_leakage(df_original, df_scrambled, ignore_value= value):

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
        valid_mask = (row_orig != ignore_value) & (row_scram != ignore_value)  
        
        # Count matches where both values are valid (not ignore_value)
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
    
   
