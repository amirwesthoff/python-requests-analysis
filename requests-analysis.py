import pandas as pd
import numpy as np
import glob
import roles
import warnings

# Disable unneccesary warning
warnings.filterwarnings("ignore")

# ---------- GLOBAL VARIABLES ---------
OUTPUT_CSV = './output.csv'
OUTPUT_XLSX = './output.xlsx'
COLUMN_HEADERS = [
    'Deadline to respond',
    'Team Request Id',
    'Team Request Name',
    'Position Name',
    'Role Notes',
    'Sales',
    'Resource Supply Chain Manager - (Contact Details)',
    'Location',
    'Required FTE',
    'Role Start Date',
    'Practice',
    'Market Unit',
]

# ---------- HELPER FUNCTIONS ---------


def createOutputFileWithHeaders(list):
    print('Creating output.csv...')

    empty_df = pd.DataFrame(columns=[COLUMN_HEADERS])
    empty_df.to_csv(OUTPUT_CSV, index=False)


def getRolesAndKeywordsRequired(selection):
    if selection == 'agile':
        roles_chosen = roles.roles_agile
    dictionary = {key: value for key,
                  value in roles.roles.items() if key in roles_chosen}
    return dictionary


def getListOfKeywords(dictionary):
    list_keywords = [value for key, value in dictionary.items()]
    return list_keywords


def flattenList(listOfLists):
    flat_list = [item for sublist in listOfLists for item in sublist]
    return flat_list

# -------------- MAIN -----------------


# Get flat list of keywords
dictionary = getRolesAndKeywordsRequired('agile')
list_of_lists = getListOfKeywords(dictionary)
flat_list = flattenList(list_of_lists)

# Convert flat list into joined string with pipe operators for pattern matching
pattern_string = "|".join(flat_list)

# Create csv file with headers
createOutputFileWithHeaders(COLUMN_HEADERS)

# Get file paths for requests
list_requests = glob.glob("requests/*.xlsx")

# Loop over each file in folder and create dataframe
for request in list_requests:
    df = pd.read_excel(request, header=5)

    # Create mask based on pattern string
    mask = df['Position Name'].str.contains(pattern_string)

    # Filter dataframe based on mask
    filtered_df = df[mask]

    # Fix line endings in column 'Role Notes'
    filtered_df['Role Notes'].replace(to_replace=[r"_x000D_"], value=[
        ""], regex=True, inplace=True)

    # filtered_df.reindex(COLUMN_HEADERS)

    # Output matches to earlier created csv file
    filtered_df.to_csv(
        OUTPUT_CSV, index=False, header=False, mode='a', encoding='utf-8')

# Open resulting output csv back as dataframe
df_new = pd.read_csv(OUTPUT_CSV, error_bad_lines=False)

# Drop duplicates based on unique Team Request Id
df_new.drop_duplicates(subset='Team Request Id', keep="first", inplace=True)

# Loop over roles and keywords in dictionary
for key, value in dictionary.items():
    # for each role, concatenate keywords into string with pipe operator for regex
    pattern_string = "|".join(value)
    # Where value in column 'Position Name' contains regex, add key as value for new column 'Label'
    df_new.loc[df_new['Position Name'].str.contains(
        pattern_string) == True, 'Label'] = key

# Format values of column 'Role Start Date' to dates
df_new['Role Start Date'] = pd.to_datetime(df_new['Role Start Date']).dt.date

# Sort by date
df_new.sort_values(by=['Role Start Date'], inplace=True)

# Perform queries

# Output to Excel file
df_new.to_excel(OUTPUT_XLSX, index=False)
