import pandas as pd
import numpy as np

df = pd.read_csv("Messy-Data.csv")

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
dfTemp = df

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
                    df.loc[idx, 'formatted_dates'] = converted_date
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


# if the cleaned temp dataSet is < original dataset score
# cleaned dataset is better quality
# if true, set df to the tempDf
if cleanedDateTimeScore < initDateTimeScore:
    df = dfTemp