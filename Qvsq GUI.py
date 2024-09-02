import pandas as pd

def clean_cnum(cnum_series):
    
    #Clean the CNUM column by stripping whitespace, converting to uppercase,
    #and removing special characters.
    return cnum_series.str.strip().str.upper()

def compare_csv(file1, file2, output_file):
    # Read the CSV files
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    
    # Ensure CNUM columns are cleaned and of the same type
    df1['CNUM'] = clean_cnum(df1['CNUM'])
    df2['CNUM'] = clean_cnum(df2['CNUM'])
    
    print(df1['CNUM'].str.contains('[^0-9A-Z]', regex=True).sum())
    print(df2['CNUM'].str.contains('[^0-9A-Z]', regex=True).sum())
    
    '''# Filter df2 for entries with Year = 2023
    if 'Year' not in df2.columns or 'CNUM' not in df2.columns:
        raise ValueError("CSV file must contain 'Year' and 'CNUM' columns")
    df2 = df2[df2['Year'] == 2023]'''

    # Print data types and some unique values
    print("df1 CNUM data type:", df1['CNUM'].dtype)
    print("df2 CNUM data type:", df2['CNUM'].dtype)
    print("Unique CNUM in df1:", df1['CNUM'].unique()[:10])
    print("Unique CNUM in df2:", df2['CNUM'].unique()[:10])

    # Filter df1 for those unique 'CNUM' values
    if 'CNUM' not in df1.columns:
        raise ValueError("CSV file must contain 'CNUM' column")
    filtered_df1 = df1[df1['CNUM'].isin(df2['CNUM'])]

    # Print shapes of DataFrames
    print("Filtered df1 shape:", filtered_df1.shape)
    print("Filtered df2 shape:", df2.shape)
    
    # Merge the filtered df1 with the filtered df2 on 'CNUM'
    merged_df = pd.merge(filtered_df1, df2, on='CNUM', suffixes=('_data1', '_data2'), how='outer', indicator=True)
    merged_df.to_csv('QvsQMergedX.csv')
    
    # Print _merge column value counts
    print("Merge indicator counts:", merged_df['_merge'].value_counts())
    
    # Identify columns to check for mismatches
    columns_to_check = [col for col in df1.columns if col != 'CNUM' and col + '_data1' in merged_df.columns]
    for column in columns_to_check:
        merged_df['mismatch_' + column] = merged_df[column + '_data1'] != merged_df[column + '_data2']
    
    # Rows with any mismatch or not found in df1
    mismatches = merged_df[(merged_df[[f'mismatch_{col}' for col in columns_to_check]].any(axis=1)) | (merged_df['_merge'] != 'both')]
    
    # Save the mismatches to CSV
    if not mismatches.empty:
        mismatches.to_csv(output_file, index=False)
        return f"Mismatches output to {output_file}"
    else:
        return "No mismatches found."

# Example usage:
file1 = '2023 Qualtrics new brand.csv'
file2 = '2023 Qualtrics old brand.csv'
output_file = 'DNO.csv'
result = compare_csv(file1, file2, output_file)
print(result)
