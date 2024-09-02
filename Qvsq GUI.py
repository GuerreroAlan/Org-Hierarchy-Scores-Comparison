import pandas as pd
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser
import os

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

'''-----------------------------------------------------------------------'''

def browse_files():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    file_entry.delete(0, tk.END)
    file_entry.insert(0, file_path)

# Set up the main application window
root = tk.Tk()
root.title("Org Hierarchy Scores Comparison v1")

#Styles
blue_btn=ttk.Style().configure("blue.btn",foreground="black",background = "#0a8fab")

# File 1 selection
file_label = tk.Label(root, text="File 1 Path:")
file_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
file_entry = tk.Entry(root, width=30)
file_entry.grid(row=0, column=1, padx=5, pady=5)
browse_button = tk.Button(root, text="Browse",command=browse_files)
browse_button.grid(row=0, column=2, padx=5, pady=5)
# File 2 selection
file_label2 = tk.Label(root, text="File 2 Path:")
file_label2.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
file_entry2 = tk.Entry(root, width=30)
file_entry2.grid(row=0, column=1, padx=5, pady=5)
browse_button2 = tk.Button(root, text="Browse",command=browse_files)
browse_button2.grid(row=0, column=2, padx=5, pady=5)

# function to enable/disable text boxes
# Domains
def EmailCheck():
    EmailCheckFlag = False
    if var_invalid_emails.get():
        EmailCheckFlag = True
    if EmailCheckFlag:
        domains_entry.configure(state='normal', foreground="black")
        domains_entry.delete(0,tk.END)
    else:
        domains_entry.delete(0,tk.END)
        domains_entry.insert(0, "Provide valid Email Domains...")
        domains_entry.configure(foreground= "gray", state='disabled')

# Unsupported Characters
def UnsupportedCharsCheck():
    UnsupportedCharsCheckFlag = False
    if var_unsupported_chars.get():
        UnsupportedCharsCheckFlag = True
    if UnsupportedCharsCheckFlag:
        user_entry_unsupported_chars.configure(state='normal', foreground="black")
        user_entry_unsupported_chars.delete(0, tk.END)
    else:
        user_entry_unsupported_chars.delete(0, tk.END)
        user_entry_unsupported_chars.insert(0, "Provide Unsupported Characters...")
        user_entry_unsupported_chars.configure(foreground= "gray", state='disabled')

# Check options
var_blank_cells = tk.BooleanVar()
var_duplicate_ids = tk.BooleanVar()
var_invalid_emails = tk.BooleanVar()
var_unsupported_chars = tk.BooleanVar()
var_excessive_lengths = tk.BooleanVar()

checks_frame = tk.LabelFrame(root, text="Select required check(s) for your participant file")
checks_frame.grid(row=3, column=0, columnspan=5, padx=15, pady=15, sticky=tk.W)

blank_cells_check = tk.Checkbutton(checks_frame, text="Check for blank cells", variable=var_blank_cells)
blank_cells_check.grid(row=1, column=0, sticky=tk.W)

duplicate_ids_check = tk.Checkbutton(checks_frame, text="Check for duplicate unique identifiers", variable=var_duplicate_ids)
duplicate_ids_check.grid(row=2, column=0, sticky=tk.W)

invalid_emails_check = tk.Checkbutton(checks_frame, text="Check for invalid and duplicate emails", variable=var_invalid_emails, command=EmailCheck)
invalid_emails_check.grid(row=3, column=0, sticky=tk.W)
# Email domains input
domains_entry = tk.Entry(checks_frame, width=40)
domains_entry.insert(0, "Provide valid Email Domains...")
domains_entry.grid(row=3, column=1, padx=5, pady=5, columnspan=3)
domains_entry.configure(foreground= "gray", state='disabled')

unsupported_chars_check = tk.Checkbutton(checks_frame, text="Check for unsupported characters", variable=var_unsupported_chars, command=UnsupportedCharsCheck)
unsupported_chars_check.grid(row=4, column=0, sticky=tk.W)
#Unsupported characters input
user_entry_unsupported_chars = tk.Entry(checks_frame, width=40)
user_entry_unsupported_chars.insert(0, "Provide Unsupported Characters...")
user_entry_unsupported_chars.grid(row=4, column=1, padx=5, pady=5, columnspan=3)
user_entry_unsupported_chars.configure(foreground= "gray", state='disabled')

excessive_lengths_check = tk.Checkbutton(checks_frame, text="Check for excessive lengths", variable=var_excessive_lengths)
excessive_lengths_check.grid(row=5, column=0, sticky=tk.W)

#LIST OF UNSUPPORTED CHARACTERS

unsupported_chars_list_frame = tk.LabelFrame(root, text = "HOW TO USE:")
unsupported_chars_list_frame.grid(row=4, column=0,columnspan=5, padx=15, pady=15, sticky=tk.W)

unsupported_chars_list_1=tk.Label(unsupported_chars_list_frame, text='1.Select the participant file to analyze. ')
unsupported_chars_list_1.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
unsupported_chars_list_3=tk.Label(unsupported_chars_list_frame, text='3.Select all the checks you need.')
unsupported_chars_list_3.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
unsupported_chars_list_2=tk.Label(unsupported_chars_list_frame, text="2.Provide valid Email Domains, (comma-separated, without '@'). ")
unsupported_chars_list_2.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
unsupported_chars_list_2=tk.Label(unsupported_chars_list_frame, text='2.Provide unsupported characters (NO comma-separated). ')
unsupported_chars_list_2.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
unsupported_chars_list_4=tk.Label(unsupported_chars_list_frame, text='4.Click "Run Check!"')
unsupported_chars_list_4.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)


# Run checks button
run_button = tk.Button(root, text="Run Checks!", command=run_checks)
run_button.grid(row=5, column=0, columnspan=2, padx=5, pady=10)

new=1
url = "https://coda.io/d/CSV-checkr_diYJsprOr4k/Team-Ideas_su-_a#_luQT9"

def openweb():
    webbrowser.open(url,new=new)

feedback_button= tk.Button(root, text ="Feedback / New ideas", command=openweb)
feedback_button.grid(row=5, column=1, columnspan=3, padx=5, pady=10)



# Start the application
root.mainloop()