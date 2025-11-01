import numpy as np
import pandas as pd
import io
from dateutil import parser
from std_columns import lst_standard_spectrumcolumn_names, standard_column_names

def svantek_dataprep(decodeddata, fileproperties, audiofolder):
    # file properties
    enc = fileproperties['encoding']
    delim = fileproperties['delim']
    skiprows = fileproperties['skiprows']

    # standard column names
    str_c_laeq1s, str_c_time, str_c_soundpath, str_c_exclude, lst_c_minmax = standard_column_names()

    # get startisodatetime when the measurement started by reading the first lines of the datafile into a very small dataframe
    df = pd.read_csv(io.StringIO(decodeddata.decode(enc)), delimiter=delim, skiprows=skiprows, nrows=1, engine="python", decimal=',')
    startisodatetime = svantek_startisodatetime(datum =df.columns[2], uur = df.columns[3])

    # read the data file, line per line and retrieve the first datarow
    all_lines = rawfile_read_all_lines(decodeddata, enc)
    first_datarow = (rawfile_determine_first_datarow(all_lines))

    # make dataframe from the lines and add isodatetime
    df = make_dataframe_from_all_lines(all_lines, first_datarow)
    df[str_c_time] = startisodatetime + pd.to_timedelta(df.index, unit='s')
    # rename and drop some columns
    df = columns_reorganize(df)
    # reorganize markers
    df = markers_reorganize(df)
    # clean order columns
    lst_standard_spectrumcolumns = lst_standard_spectrumcolumn_names()
    lst_always = [str_c_time, str_c_laeq1s, str_c_exclude, 'm2', 'm3', 'm4', str_c_soundpath]
    lst_always.extend(lst_standard_spectrumcolumns)
    df = df[lst_always]
    return df

def svantek_startisodatetime(datum, uur):
    datum = (datum[2:-1])
    uur = uur[2:-1]
    datumuur = datum + ' ' + uur
    datumuur = parser.parse(datumuur, yearfirst=True)
    return datumuur

def rawfile_read_all_lines(decoded, enc):
    try:
        datalines = decoded.decode(enc).splitlines()
    except UnicodeDecodeError:
        datalines = decoded.decode('utf-8', errors='ignore')
    return datalines
def rawfile_determine_first_datarow(all_datalines):
    first_datarow = 0
    for line in all_datalines:
        if line[:6] == "//rec.":
            print('first dataline in line:', line)
            return first_datarow
        first_datarow = first_datarow + 1
    return first_datarow
def extract_records(all_lines, first_datarow):
    """
    Splits de inputlijst in records. Elke record start bij '//rec.'.
    Retourneert een lijst van lijsten met datawaarden.
    """
    records = []
    current_record = []

    for item in all_lines[first_datarow:]:
        item = item.strip()

        if item.startswith('//rec.'):
            if current_record:
                records.append(current_record)
            current_record = [item]
        else:
            values = [v.strip() for v in item.split(',') if v.strip()]
            current_record.extend(values)

    if current_record:
        records.append(current_record)

    return records

def normalize_records(records):
    """
    Zorgt ervoor dat alle records even lang zijn door lege strings toe te voegen.
    Retourneert een genormaliseerde lijst van records.
    """
    max_len = max(len(r) for r in records)
    return [r + [''] * (max_len - len(r)) for r in records]

def make_dataframe_from_all_lines(all_lines, first_datarow):
    """
    Hoofdfunctie die een DataFrame maakt uit een lijst van strings.
    Elke record wordt een rij, en data wordt opgesplitst in kolommen.
    """
    records = extract_records(all_lines, first_datarow)
    padded_records = normalize_records(records)
    column_names = [f'col_{i}' for i in range(len(padded_records[0]))]
    df = pd.DataFrame(padded_records, columns=column_names)
    return df
def columns_reorganize(df):
    # drop useless columns
    columns_to_drop = ['col_0', 'col_2','col_3', 'col_34', 'col_35', 'col_36']
    df = df.drop(columns=columns_to_drop)
    # rename spectral
    old_names = ['col_4', 'col_5', 'col_6', 'col_7', 'col_8', 'col_9', 'col_10', 'col_11', 'col_12', 'col_13', 'col_14', 'col_15', 'col_16', 'col_17', 'col_18', 'col_19', 'col_20', 'col_21', 'col_22', 'col_23', 'col_24', 'col_25', 'col_26', 'col_27', 'col_28', 'col_29', 'col_30', 'col_31', 'col_32', 'col_33']
    new_names =  lst_standard_spectrumcolumn_names()
    column_mapping  = dict(zip(old_names,new_names))
    df = df.rename(columns=column_mapping)
    # rename laeq1s
    str_c_laeq1s, str_c_time,  str_c_soundpath,str_c_exclude, lst_c_minmax = standard_column_names()
    df = df.rename(columns={'col_1':str_c_laeq1s})
    return df
def markers_reorganize(df):
    '''the 4 available markers in a svantek955 are all in one column, eg: 8001, 8002, 8004, 8008.
    this function reorganizes the marker data in 4 columns m1, m2, m3 and m4'''
    # add helper columns m1, m2, m3, m4, counter and a reset
    df = markers_makehelpercolumns(df)
    # make a marker summary in a small tmpdf
    tmpdf = markers_makesummary(df)
    # determine m1, m2, m3 and m4 - marker update instructions based on the summary
    lst_markerupdate_instructions = markers_update_instructions(tmpdf)

    for update in lst_markerupdate_instructions:
        startindex = update[0]
        stopindex = update[1]
        markerindex = update [2]
        markercolumn = 'm' + str(markerindex)
        df.loc[startindex:stopindex, markercolumn] = 1
    df = df.drop(columns=['col_37'])
    str_c_laeq1s, str_c_time, str_c_soundpath, str_c_exclude, lst_c_minmax = standard_column_names()
    df = df.rename(columns={'m1': str_c_exclude})
    df[str_c_soundpath]='0'
    return df
def markers_makesummary(df):
    '''make a small temporary dataframe with all the information needed to analyse the markers
    :parameter: complete dataframe
    :return: small dataframe '''
    df = df[['mnr', 'm1', 'm2', 'm3', 'm4', '#', 'reset']]
    filtered_df = df[df.iloc[:, 0].notna()]
    filtered_df = filtered_df.iloc[:, [0, 1,2,3,4,5,6]]
    return filtered_df
def markers_update_instructions(tmpdf):
    '''
    :parameter: small summary-dataframe which contains all the necessary data of the markers
    :return: list with update instructions'''
    lst=[]
    for index, row in tmpdf.iterrows():
       if row['mnr'] == 0:
            tmpdf.loc[index, '#'] = 0
       elif row['mnr'] != 0:
            # check if the mnr is equal to a resetvalue. if there is not found a resetvalue, then make updatelist, else do almost nothing...
            bestaatereenreset = markers_find_greatest_reset_index(tmpdf, index, row['mnr'])
            if bestaatereenreset is None:
                markernumber =row['mnr'] - tmpdf.loc[index, '#']
                markerindex = markers_find_marker_index(markernumber)
                aant_lopende_markers =  tmpdf.loc[index, '#'] + 1
                tmpdf.loc[index, '#'] = aant_lopende_markers
                resetvalue = tmpdf.loc[index, '#'] - 1
                tmpdf.loc[index, 'reset'] = resetvalue
                startindex = index
                stopindex = markers_find_stopindex(tmpdf, startindex, resetvalue)
                updateinstructielijstje = [startindex, stopindex, markerindex]
                tmpdf.loc[startindex:stopindex,'#'] = aant_lopende_markers
                lst.append(updateinstructielijstje)
            else: # de markernummer is een resetwaarde van een eerder geactiveerde marker, do almost nothing
                aant_lopende_markers = tmpdf.loc[index, '#']
                tmpdf.loc[index,'#'] = aant_lopende_markers - 1
                tmpdf.loc[index, 'reset'] = 0
    return lst
def markers_find_marker_index(marker_value):
    """
    Finds the 1-based index of a specific marker value within marker_list (list):
    The list of markers ([1, 2, 4, 8]).
    :parameter:

        marker_value (int): The specific marker value to find.
    :returns:
        int: The 1-based index (1, 2, 3, or 4), or None if the value is not found.
    """
    marker_list = [1,2,4,8]
    try:
        # 1. Use the .index() method to find the 0-based position
        zero_based_index = marker_list.index(marker_value)

        # 2. Add 1 to convert to the desired 1-based index
        one_based_index = zero_based_index + 1

        return one_based_index

    except ValueError:
        # Handle the case where the marker_value is not in the list
        return None
def markers_find_stopindex(df: pd.DataFrame, current_index: int, resetvalue: int):
    """
    Finds the index of the first (smallest index value) record where the
    index is greater than the current_index AND the 'mnr' column is equal to resetvalue.

    :parameter:
        df: The input pandas DataFrame with numerical indices.
        current_index: The starting index threshold (e.g., 7).
        resetvalue: where the marker is resetted and thus stops
    :returns:
        The matching index (int) or None if no record is found.
    """

    # 1. Define the two conditions using boolean masks (vectorized operation)
    # Condition 1: Index value > current_index
    condition_index = df.index > current_index

    # Condition 2: 'mnr' column value is 0.0
    # Note: We ensure the column is treated as numeric (float) for comparison
    condition_mnr = df['mnr'].astype(float) == resetvalue

    # 2. Combine the conditions using the AND operator (&)
    combined_condition = condition_index & condition_mnr

    # 3. Filter the DataFrame to only include rows that meet both conditions
    matching_records = df[combined_condition]

    # 4. Check if any records were found and return the first index
    if not matching_records.empty:
        # Since the index is already sorted (it's the DataFrame index),
        # the first element of the index is the smallest matching index.
        return int(matching_records.index[0])
    else:
        # Return None if no record matches the criteria
        return None

def markers_makehelpercolumns(df):
    # make a number - based marker from the raw data
    df['mnr'] = df['col_37'].str[4:7]
    # 2. Converteer de kolom naar numeriek (float, omdat integers geen NaN kunnen bevatten)
    # 'errors="coerce"' zet alle waarden die NIET kunnen worden geconverteerd naar NaN.
    df['mnr'] = pd.to_numeric(df['mnr'], errors='coerce')
    df['m1'] = np.nan
    df['m2'] = np.nan
    df['m3'] = np.nan
    df['m4'] = np.nan
    df['#'] = 0
    df['reset'] = np.nan

    return df


def markers_find_greatest_reset_index(df: pd.DataFrame, current_index: int, reset_value: float):
    """
    Finds the largest index value (row label) that is strictly less than current_index AND
    where the 'reset' column value equals reset_value.
    :parameter:
        df: The pandas DataFrame containing the data. The index is used for comparison.
        current_index: The upper limit (exclusive) for the index search. Must be an integer.
        reset_value: The specific value to match in the 'mnr' column.
    :returns:
        The greatest index value (label) that meets the criteria, or None if no
        such record is found.
    """

    # 1. Define the two conditions using boolean masks (vectorized operation)
    # Condition 1: Index value < current_index (strictly smaller)
    condition_index = df.index < current_index

    # Condition 2: 'mnr' column value is equal to reset_value
    condition_mnr = df['reset'] == reset_value

    # 2. Combine the conditions using the AND operator (&)
    combined_condition = condition_index & condition_mnr

    # 3. Filter the DataFrame to only include rows that meet both conditions
    matching_records = df[combined_condition]

    # 4. Check if any records satisfy both conditions
    if matching_records.empty:
        # DEBUG : No records found matching the criteria
        # print(f"No previous record found with index < {current_index} and mnr == {reset_value}")
        return None
    else:
        # 5. Find the maximum index value (the greatest index) from the result
        # We convert the maximum index to int explicitly.
        greatest_index = int(matching_records.index.max())
        return greatest_index