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


def processRequestFiles(list_requests):
    print('Processing files...')
    counter = 0
    num_files = len(list_requests)
    for request in list_requests:
        df = pd.read_excel(request, header=5)

        # Create mask based on pattern string
        mask = df['Position Name'].str.contains(pattern_string)

        # Filter dataframe based on mask
        filtered_df = df[mask]

        if not filtered_df.empty:
            hits = filtered_df.shape[0]
            counter += hits
            print('Found %d hit(s)...' % hits)

        # Fix line endings in column 'Role Notes'
        filtered_df['Role Notes'].replace(to_replace=[r"_x000D_"], value=[
            ""], regex=True, inplace=True)

        # filtered_df.reindex(COLUMN_HEADERS)

        # Output matches to earlier created csv file
        filtered_df.to_csv(
            OUTPUT_CSV, index=False, header=False, mode='a', encoding='utf-8')

    print('Processing completed. %d file(s) processed, %d hit(s) found.' %
          (num_files, counter))


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


def addLabels():
    # Loop over roles and keywords in dictionary
    print('Adding labels...')
    for key, value in dictionary.items():
        # for each role, concatenate keywords into string with pipe operator for regex
        pattern_string = "|".join(value)
        # Where value in column 'Position Name' contains regex, add key as value for new column 'Label'
        df.loc[df['Position Name'].str.contains(
            pattern_string) == True, 'Label'] = key


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

# Process files at file paths
processRequestFiles(list_requests)

# Open resulting output csv back as dataframe, skip over bad input
df = pd.read_csv(OUTPUT_CSV, error_bad_lines=False)

# Drop duplicates based on unique Team Request Id
dropDuplicateRequests(df)

# Add label to requests based on keywords for each role
addLabels()

# Format values of column 'Role Start Date' to dates
print('Formatting column "Role Start Date"...')
df['Role Start Date'] = pd.to_datetime(df['Role Start Date']).dt.date

# Sort by date
print('Sorting by date...')
df.sort_values(by=['Role Start Date'], inplace=True)

# Perform queries

# Output to Excel file
print('Generating Excel file...')
df.to_excel(OUTPUT_XLSX, index=False)
