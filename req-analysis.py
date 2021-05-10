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


def getRolesAndKeywordsRequired(selection):
    print('Getting required roles and keywords...')
    if selection == 'agile':
        roles_chosen = roles.roles_agile
    dictionary = {key: value for key,
                  value in roles.roles.items() if key in roles_chosen}
    return dictionary


def getListOfKeywords(dictionary):
    # print('Getting list of keywords...')
    list_keywords = [value for key, value in dictionary.items()]
    return list_keywords


def flattenList(listOfLists):
    # print('Flattening list...')
    flat_list = [item for sublist in listOfLists for item in sublist]
    return flat_list


def processRequests(list_requests):
    print('Creating empty dataframe...')
    # Create empty dataframe with headers
    df = pd.DataFrame(columns=COLUMN_HEADERS)

    print('Adding requests to empty dataframe...')
    # Create temporary list to hold rows
    L = []
    # Loop over files
    for request in list_requests:
        # Create temporary dataframe
        df_temp = pd.read_excel(request, header=5)
        # Append temporary dataframe to temporary list
        L.append(df_temp)

    # Concatenate temporary lists to empty datamframe
    df = pd.concat(L, ignore_index=True)

    return df


def dropDuplicateRequests(df):
    print('Dropping duplicate requests...')
    # Get length of original dataframe
    rows_df = df.shape[0]
    # Drop duplicates based on Team Request Id
    df_no_dupes = df.drop_duplicates(
        subset='Team Request Id', keep="first")
    # Get length of dataframe without duplicates
    rows_df_no_dupes = df_no_dupes.shape[0]
    # Calculate difference
    num_duplicates = rows_df - rows_df_no_dupes
    print('Dropped %d duplicate(s).' % (num_duplicates))

    return df_no_dupes


def addLabels(df):
    # Loop over roles and keywords in dictionary
    print('Adding labels...')
    for key, value in dictionary.items():
        # for each role, concatenate keywords into string with pipe operator for regex
        pattern_string = "|".join(value)
        # Where value in column 'Position Name' contains regex, add key as value for new column 'Label'
        df.loc[df['Position Name'].str.contains(
            pattern_string) == True, 'Label'] = key
    return df

# -------------- MAIN -----------------


# Get flat list of keywords
dictionary = getRolesAndKeywordsRequired('agile')
list_of_lists = getListOfKeywords(dictionary)
flat_list = flattenList(list_of_lists)

# Convert flat list into joined string with pipe operators for pattern matching
pattern_string = "|".join(flat_list)

# Get file paths for requests
list_requests = glob.glob("requests/*.xlsx")

# Add all requests to a single dataframe
df = processRequests(list_requests)

# Drop columns with headers containing 'Unnamed'
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# Drop coluumn 'Deadline to respond'
df = df.drop('Deadline to respond', axis=1)

# Drop duplicate requests
df = dropDuplicateRequests(df)

# Add labels
df = addLabels(df)

# Format values of column 'Role Start Date' to dates
print('Formatting column "Role Start Date"...')
df['Role Start Date'] = pd.to_datetime(df['Role Start Date']).dt.date

# Sort by date
print('Sorting by date...')
df.sort_values(by=['Role Start Date'], inplace=True)

# Generate Excel
df.to_excel(OUTPUT_XLSX, index=False)

# Fix line endings in column 'Role Notes'
df['Role Notes'].replace(to_replace=[r"_x000D_"], value=[
    ""], regex=True, inplace=True)

# Generate csv
df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')
