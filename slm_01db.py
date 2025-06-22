import numpy as np
import pandas as pd
from  std_columns import (standard_column_names, lst_standard_spectrumcolumn_names,
                          standardize_minmaxdata, lst_spectra_spellings, col_lst_always)
from dateutil import parser
import io
from datetime import datetime
import os
def zero1db_dataprep(decodeddata:str, fileproperties, audiofolder):
    enc = fileproperties['encoding']
    delim = fileproperties['delim']
    skiprows = fileproperties['skiprows']
    #the first row contains rubbish, but the date is there...
    df = pd.read_csv(io.StringIO(decodeddata.decode(enc)), nrows= 0, delimiter=delim, engine="python", decimal='.')
    datum = df.columns.tolist()[-1]
    datum = parser.parse(datum, dayfirst=True)
    # read complete dataframe
    df = pd.read_csv(io.StringIO(decodeddata.decode(enc)), delimiter=delim, skiprows=skiprows, skipfooter = 96, engine="python", decimal=',')
    # get standard columnames
    str_c_laeq1s, str_c_time, str_c_soundpath, str_c_exclude, lst_strminmax = standard_column_names()
    # solve date time issues
    df['time_parsed'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.time
    df['date']= datum
    df['datetime'] = df.apply(lambda row: datetime.combine(row['date'], row['time_parsed']), axis=1)
    df = df.drop(['time_parsed','date','Time'],axis=1)
    # standard names
    df.rename(columns={'datetime': str_c_time}, inplace=True)
    df.rename(columns={'LAeq': str_c_laeq1s}, inplace=True)
    # get interesting fields
    lst_flds_a = col_lst_always(str_c_time, str_c_laeq1s)
    # min max  columns
    lst_flds_minmax = []  # no minmax fields
    df, containsminmax = standardize_minmaxdata(df)
    if containsminmax: lst_flds_minmax = lst_strminmax  # minmax
    # spectrumcolumns
    lst_standaardspectrumkolomnamen = lst_standard_spectrumcolumn_names()
    for c in df.columns.tolist():
        for lst_sp in lst_spectra_spellings():
            if c in lst_sp:
                freqindx = (lst_sp.index(c))  # get index of columname that is found
                # rename with corresponding index from the standard column-names
                df.rename(columns={c: lst_standaardspectrumkolomnamen[freqindx]}, inplace=True)
    df[str_c_exclude]=np.nan
    df[str_c_soundpath] = ''
    df['sound']= np.nan
    lst_interesting = lst_flds_a + lst_flds_minmax + lst_standaardspectrumkolomnamen + [str_c_soundpath] + ['sound'] + [str_c_exclude]
    df = df[lst_interesting]
    # update soundpath and the marker sound if an audiofolder name is valid
    df = update_soundpath_and_soundmarker(df, audiofolder, datum)

    return df
def update_soundpath_and_soundmarker(df, audiofolder, datum):
    if not audiofolderisvalid(audiofolder):
        return df  # do nothing if folder is invalid
    # Create DataFrame from audio file time ranges
    updates = maaktijdslijstaudio(datum, audiofolder)
    audio_df = pd.DataFrame(updates, columns=['start', 'stop', 'soundpath'])
    # Sort both DataFrames by time for merge_asof
    df = df.sort_values('isodatetime')
    audio_df = audio_df.sort_values('start')

    # Use merge_asof to align each row with the closest audio start time
    df = pd.merge_asof(df, audio_df, left_on='isodatetime', right_on='start', direction='backward')
    # filtered_df = df[(df['isodatetime'] >= '2025-05-26 09:30:00') & (df['isodatetime'] <= '2025-05-26 09:30:35')]
    # filtered_df = filtered_df[['isodatetime', 'sound', 'soundpath_x', 'soundpath_y']]
    # Mark rows where isodatetime is within the audio interval
    df['sound'] = df.apply(
        lambda row: 1 if pd.notnull(row['stop']) and row['start'] <= row['isodatetime'] <= row['stop'] else np.nan,
        axis=1)

    mask = (df['sound'] == 1.0) & (df['soundpath_y'].notna())

    # Identify the start of each block of True values in the mask
    block_start = (mask != mask.shift(fill_value=False)) & mask

    # Get the index of the first row in each valid block
    first_indexes = df.index[block_start].tolist()

    # Create the new column filled with nothing
    df['soundpath_z'] = ''

    # Set only that first match
    df.loc[first_indexes, 'soundpath_z'] = df.loc[first_indexes, 'soundpath_y']

    # Drop helper columns
    df.drop(columns=['start', 'stop', 'soundpath_x', 'soundpath_y'], inplace=True)
    df.rename(columns={'soundpath_z': 'soundpath'}, inplace=True)
    df['soundpath'] = df['soundpath'].replace('', np.nan)
    return df
def maaklijstaudio(folderpth):
    '''makes a file list of mp3's that are in a folder'''
    lst_mp3 =[]
    for file in os.listdir(folderpth):
        if file.lower().endswith('.mp3'):
            lst_mp3.append(file)
    return lst_mp3
def maaktijdslijstaudio(datum, folderpth):
    ''' The mp3's have a fixed filename - string - that represents the starttime, stoptime of the file.
    A list of filenames is made and transformed into another
    list with the timestamps starttime, stoptime with corresponding .mp3
    :param:
        datum: to make the datetime notation in isoformat
        folderpath: here are the mp3's
    :returns: list (starttime, stoptime, mp3name)
    '''
    lst_mp3=maaklijstaudio(folderpth)
    lst_isodatetime_start=[]
    lst_isodatetime_stop = []
    for mp3 in lst_mp3:
        timed_start = mp3[0:6]
        timed_stop = mp3[7:13]
        formatt = '%H%M%S'
        timed_start = datetime.strptime(timed_start, formatt).time()
        isodatetime_start = datetime.combine(datum,timed_start)
        lst_isodatetime_start.append(isodatetime_start)

        timed_stop = datetime.strptime(timed_stop, formatt).time()
        isodatetime_stop = datetime.combine(datum, timed_stop)
        lst_isodatetime_stop.append(isodatetime_stop)
    return list(zip(lst_isodatetime_start,lst_isodatetime_stop,lst_mp3))
def audiofolderisvalid(audiofolder):
    folderisvalid = False
    if audiofolder == "":
        return folderisvalid
    if os.path.isdir(audiofolder):
        folderisvalid = True
    return folderisvalid
