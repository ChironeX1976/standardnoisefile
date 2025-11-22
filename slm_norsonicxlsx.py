import numpy as np
import pandas as pd
from io import BytesIO
from dateutil import parser
from std_columns import lst_standard_spectrumcolumn_names, standard_column_names
import re

def norsonic140xlsx_dataprep(decodeddata, fileproperties, lst_audiofiles):
    # standard column names
    str_c_laeq1s, str_c_time, str_c_soundpath, str_c_exclude, lst_c_minmax = standard_column_names()

    skiprows = 0
    column_indexes_to_keep = []

    # cols to keep based on the first row
    df = pd.read_excel(BytesIO(decodeddata), sheet_name='Summary', skiprows=skiprows)
    lst_interesting = ['Time', 'LAeq']
    for interest in lst_interesting:
        indices_1 = find_column_index(df, interest, False)
        if indices_1:
            column_indexes_to_keep.extend(indices_1)
        else:
            print("No matching columns found.\n")

    # cols to keep based on the second row
    skiprows = fileproperties['skiprows']-1
    df = pd.read_excel(BytesIO(decodeddata), sheet_name='Summary', skiprows=skiprows)
    lst_interesting = ['A']
    for interest in lst_interesting:
        indices_1 = find_column_index(df, interest, True)
        if indices_1:
            column_indexes_to_keep.extend(indices_1)
        else:
            print("No matching columns found.\n")

    # cols to keep based on the third row
    skiprows = fileproperties['skiprows']
    df = pd.read_excel(BytesIO(decodeddata), sheet_name='Summary', skiprows =skiprows )
    lst_interesting = ['hz']
    for interest in lst_interesting:
        indices_1 = find_column_index(df, interest, False)
        if indices_1:
            column_indexes_to_keep.extend(indices_1)
        else:
            print("No matching columns found.\n")


    if column_indexes_to_keep:
        columns_to_keep_names = [df.columns[i] for i in column_indexes_to_keep]
        df = df[columns_to_keep_names]
    else:
        print("Warning: column_indexes_to_keep is empty. Returning an empty DataFrame.")
        df = df.iloc[:, 0:0]


    df.rename(columns={df.columns[0]: str_c_time}, inplace=True)
    df.rename(columns={df.columns[1]: str_c_laeq1s}, inplace=True)
    df.rename(columns={df.columns[2]: 'sound'}, inplace=True)

    df[str_c_time] = df[str_c_time].astype(str).str.strip('()')
    df[str_c_time] = pd.to_datetime(df[str_c_time], errors='coerce')

    df.loc[df['sound'] == 'A', 'sound'] = 1

    # rename spectral
    old_names = ['25 Hz', '31.5 Hz', '40 Hz', '50 Hz', '63 Hz', '80 Hz', '100 Hz', '125 Hz', '160 Hz', '200 Hz',
                 '250 Hz', '315 Hz', '400 Hz', '500 Hz', '630 Hz', '800 Hz', '1.0 kHz', '1.25 kHz', '1.6 kHz',
                 '2.0 kHz', '2.5 kHz', '3.15 kHz', '4.0 kHz', '5.0 kHz', '6.3 kHz', '8.0 kHz', '10.0 kHz', '12.5 kHz',
                 '16.0 kHz', '20.0 kHz']
    lst_standard_spectrumcolumns = lst_standard_spectrumcolumn_names()
    column_mapping = dict(zip(old_names, lst_standard_spectrumcolumns))
    df = df.rename(columns=column_mapping)
    # add some mandatory columns
    df[str_c_exclude]=np.nan
    df[str_c_soundpath] = np.nan
    lst_always = [str_c_time, str_c_laeq1s, str_c_exclude, 'sound', str_c_soundpath]
    lst_always.extend(lst_standard_spectrumcolumns)
    df = df[lst_always]
    df = organize_soundpaths(df, lst_audiofiles)
    return df


def find_column_index(df: pd.DataFrame, search_term: str, exact_match: bool = False) -> list[int]:
    """
    Searches for the indices of all column names in a Pandas DataFrame.
    The matching behavior is controlled by the 'exact_match' flag.

    Args:
        df: The Pandas DataFrame whose columns will be searched.
        search_term: The substring (or exact column name) to look for.
        exact_match: If True, the column name must exactly match the
                     search_term (case-insensitive). If False (default),
                     the column name must merely contain the search_term.

    Returns:
        A list of 0-based integer indices where the match was found.
        Returns an empty list if no matches are found.
    """

    # 1. Extract column names from the DataFrame
    column_names = df.columns.tolist()

    matching_indices = []
    # 2. Prepare the search term for case-insensitive comparison
    lower_search_term = search_term.lower()

    # 3. Iterate through ALL column names
    for index, name in enumerate(column_names):
        lower_name = name.lower()

        is_match = False

        if exact_match:
            # Check for exact match (case-insensitive)
            if lower_name == lower_search_term:
                is_match = True
        else:
            # Check for substring containment (case-insensitive)
            if lower_search_term in lower_name:
                is_match = True

        if is_match:
            matching_indices.append(index)

    # 4. Return the list of all matching indices (which may be empty)
    return matching_indices

def organize_soundpaths (df, lstaudiofiles):
    df['sound'] = pd.to_numeric(df['sound'], errors = 'coerce')
    # maak een hulp kolom die een kopie is van de sound-kolom, maar 1 rij naar beneden geshift
    df['previoussoundrow']= df['sound'].shift(1).fillna(0)
    # als er sound is op een moment = 1 , en de previoussoundrow was er geen sound = 0: dan is dat een moment dat de audio gestart werd
    df['startaudio'] = (df['sound'] == 1) & (df['previoussoundrow'] == 0)
    # de hoeveelste audiofile berekenen
    df['audiofilenumberseries'] = df['startaudio'].cumsum()
    df['audiofilenumberstart'] = df['audiofilenumberseries'].where(df['startaudio']==True)
    df['audiofilenumber']= df['audiofilenumberstart'] -1
    df.drop(columns=['previoussoundrow', 'startaudio', 'audiofilenumberseries','audiofilenumberstart' ], axis=1, inplace=True)

    dct_filenameandnumber = create_indexed_file_list((lstaudiofiles))
    dfsound = pd.DataFrame(list(dct_filenameandnumber.items()), columns=['audiofilenumber', 'audiofilename'])
    df = pd.merge(df, dfsound, on='audiofilenumber', how='left')
    df['soundpath'] = df['audiofilename']
    df.drop(columns=['audiofilenumber', 'audiofilename'], axis=1, inplace=True)
    return df


def create_indexed_file_list(file_list):
    """
    Parses a list of filenames, extracts the R-number index, and organizes
    the files into a nested list structure based on that index.

    The index is extracted from the 'Rxxxxxxx.WAV' part of the filename.

    Args:
        file_list (list): A list of strings representing the file names.

    Returns:
        dictionary with the filenumber and the filename.
    """
    file_map = {}
    max_index = -1

    # 1. Parse and map files to their index
    for filename in file_list:
        # Regular expression to find the numeric part immediately after 'R'
        # and before '.WAV', even if the extension is different.
        match = re.search(r'_R(\d+)\.', filename)

        if match:
            # Extract the matched group (the numbers) and convert to integer
            index = int(match.group(1))

            # Store the file in a dictionary mapping index -> filename
            file_map[index] = filename

            # Keep track of the largest index encountered
            if index > max_index:
                max_index = index
        else:
            print(f"Warning: Could not extract index from filename: {filename}")

    return file_map
