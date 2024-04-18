
import pandas as pd
import ipywidgets as widgets

# from IPython.display import display

# look for redundancy and nulls in rows
# uniformity score by column, column least uniform is edited first
# penalize missing values and redundancy, while giving credit for uniformity
# in the form of data

# the column is (mostly) empty, has some constant value throughout, is a
# duplicate of another column
dropColumnScore = 0
# the row is mostly empty, or it is a duplicate of another row
dropRowScore = 0
#
missingValueScore = 0
# This operator indicates the column whose string values can be split to create
# multiple new columns
splitColumnScore = 0

# drop column, drop row, fill in missing values, split on delimiter,
df = pd.read_csv("Messy-Data.csv")

# loop to look for columns with same values throughout/ is a duplicate of another column
# for i, column1 in enumerate(df.columns):
#     for column2 in df.columns[i+1]:

        # jaccard comparison
        # A = column1.intersection(column2)
        # B = column1.union(column2)
        # if(float(len(A))/float(len(B)) > 0.85) :
        #     dropColumnScore += 1

# loop to find empty rows/ duplicate rows
# loop to find missing values (MAR, MNAR, MCAR
# loop to find columns that can be split on a delimeter

