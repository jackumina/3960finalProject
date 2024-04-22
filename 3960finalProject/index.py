import pandas as pd
import numpy as np
import ipywidgets as widgets
from IPython.display import display
import io

#########################
# Code to upload a file
#
#########################
# # Create a FileUpload widget to allow users to upload CSV files
# upload = widgets.FileUpload(
#     accept='.csv',  # Accept only CSV files
#     multiple=False,  # Allow only one file at a time
#     description='Upload CSV',  # Button label
#     button_style='info'  # Optional: makes the button blue
# )

# # Define a global variable to hold the DataFrame
# df = None  # Start with an empty variable

# # Define a function to handle file uploads and set 'df' to the uploaded data
# def on_file_upload(change):
#     global df  # Use global keyword to indicate that we're referring to the global variable

#     uploaded_files = change['new']  # Get the uploaded file(s)

#     if len(uploaded_files) > 0:
#         # Get the first uploaded file (assuming multiple=False)
#         filename = list(uploaded_files.keys())[0]
#         content = uploaded_files[filename]['content']  # File content as bytes

#         # Read the content into a Pandas DataFrame
#         df = pd.read_csv(io.BytesIO(content))  # Read from bytes

#         print(f"CSV file '{filename}' has been loaded into 'df':")
#         # display(df)  # Show the DataFrame content to confirm success

# # Attach the callback function to the FileUpload widget
# upload.observe(on_file_upload, names='value')
#######################################

# you can change the file by hardcoding the file name here
df = pd.read_csv("Messy-Data.csv")
# df = pd.read_csv("Untitled.csv")

# get initial data quality score
wrangling_score_datetime = {}

# List of expected date formats
possible_formats = [
    '%dst %B, %Y',  # DDst monthname, YYYY (1st December, 1984)
    '%dnd %B, %Y',  # DDnd monthname, YYYY (2nd December, 1984)
    '%drd %B, %Y',  # DDrd monthname, YYYY (23rd December, 1984)
    '%dth %B, %Y',  # DDth monthname, YYYY (15th December, 1984)
    '%m/%d/%y',  # MM/DD/YY (5/21/80)
    '%m.%d.%Y',  # MM.DD.YYYY (03.10.1978)
    '%d.%m.%Y',  # DD.MM.YYYY (15.06.1996)
    '%d-%B-%y',  # DD-monthname-YY (21-May-71)
    '%m-%d-%Y',  # MM-DD-YYYY (02-01-2021)
    '%d/%m/%Y',  # DD/MM/YYYY (19/07/1972)
    '%d-%b-%y',  # DD-monthabb-YY(18-Nov-86)
    '%d-%m-%Y',  # DD-MM-YYYY (27-03-1985)
]

# Holds bools of if to_dateTime can be applied to column
# holds datasets data quality score
date_column_status = {}
initDateTimeScore = 0

#########################
# get columns that can be cleaned with to_datetime
# and get the datasets initial data quality score
#########################
for col in df.columns:
    column_values = df[col]
    # 0's based (will be 1 less than what's in the table)
    date_count = 0
    total_count = len(column_values)

    # Check each value in the column to see if it's a valid date
    for val in column_values:
        # Loop through the possible formats and attempt to parse the dates
        for fmt in possible_formats:
            try:
                # if value is nan
                if pd.isna(val):
                    break
                # Try to convert the value to datetime with the current format
                pd.to_datetime(val, format=fmt, errors='raise')
                date_count += 1
                initDateTimeScore += 1
                break
            except ValueError as e:
                continue  # If it fails, continue to the next format

    # Determine if a large proportion of the column consists of dates
    if date_count / total_count >= 0.75:  # Example threshold
        date_column_status[col] = True
    else:
        date_column_status[col] = False

wrangling_score_datetime[0] = initDateTimeScore
#######################################


#########################
# makes a temp dataset and applies the to_datetime conversions
# to the columns specified as true above
#########################
dfTemp = df.copy()

for col in date_column_status:
    value = date_column_status[col]
    if value:
        # Initialize the new column with NaT (Not a Time)
        dfTemp['formatted_dates'] = np.datetime64('NaT')
        # print(col)

        for idx, val in enumerate(dfTemp[col]):
            # print(val)
            # for val in key:
            for fmt in possible_formats:
                try:
                    # If successful, assign the converted value to the new column
                    converted_date = pd.to_datetime(val, format=fmt, errors='raise')
                    dfTemp.loc[idx, 'formatted_dates'] = converted_date
                    break  # Break if successful to avoid double attempts
                except ValueError:
                    continue  # Continue to the next format

        dfTemp[col] = dfTemp['formatted_dates']
        del dfTemp['formatted_dates']
#######################################


#########################
# check the data quality of the cleaned temp dataset
#
#########################
# holds cleaned datasets data quality score
# Define a specific datetime format to check against
cleanedDateTimeScore = 0
target_format = '%Y-%m-%d'  # YYYY-MM-DD

for col in date_column_status:
    value = date_column_status[col]
    if value:
        for idx, val in enumerate(dfTemp[col]):
            try:
                # Try to convert the value to datetime with the given format
                pd.to_datetime(val, format=target_format, errors='raise')
            except ValueError:
                cleanedDateTimeScore += 1  # If there's a ValueError, it doesn't match
                continue
#######################################


#########################
# Creates the UI for the program
# creates the dropdown and the save button for the UI
#########################
# if the cleaned temp dataSet is < original dataset score
# cleaned dataset is better quality
# if true, set df to the tempDf
if cleanedDateTimeScore < initDateTimeScore:
    # Create a dropdown widget
    dropdown = widgets.Dropdown(
        options=["Select cleaning method...", "Clean rows with to_datetime", "none"],  # The available options
        # value="Select cleaning method...",  # The default selected value
        description="Choose from cleaning suggestions:", )  # Label for the dropdown
else:
    # Create a dropdown widget
    dropdown = widgets.Dropdown(
        options=["Select cleaning method...", "none", "Clean rows with to_datetime"],  # The available options
        # value="Select cleaning method...",  # The default selected value
        description="Choose from cleaning suggestions:", )  # Label for the dropdown

# Create an output widget to display the dataset
output = widgets.Output()


# Define a callback function that updates the output when the dropdown changes
def on_dropdown_change(change):
    # Get the new value from the dropdown
    new_value = change['new']

    with output:
        output.clear_output()  # Clear any previous output

        if new_value == "Clean rows with to_datetime":
            global df  # Indicate that we're referencing the global variable
            df = dfTemp  # Assign the global variable to dfTemp
            display(df)
        elif new_value == "none":
            display(df)


# Connect the callback function to the dropdown's 'value' attribute
dropdown.observe(on_dropdown_change, names="value")

# Create a button widget
save_button = widgets.Button(
    description='Save Data',
    tooltip='Click to save the dataset to a CSV file',
    button_style='success'  # Green button
)


# Define a callback function that saves the DataFrame to a CSV file
def save_to_csv(button):
    filename = 'saved_dataset.csv'  # Name of the CSV file
    df.to_csv(filename, index=False)  # Save the DataFrame without the index

    # Inform the user that the file has been saved
    print(f"Dataset has been saved to '{filename}'.")


# Attach the callback function to the button
save_button.on_click(save_to_csv)

# # Display the dropdown and the output widget
display(dropdown, save_button, output)
#######################################
