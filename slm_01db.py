import numpy as np
import pandas as pd
from  std_columns import standard_column_names, lst_standard_spectrumcolumn_names,  standardize_minmaxdata, lst_spectra_spellings
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
    df[str_c_soundpath] = ''
    df['sound']= np.nan
    lst_interesting = lst_flds_a + lst_flds_minmax + lst_standaardspectrumkolomnamen + [str_c_soundpath] + ['sound']
    df = df[lst_interesting]
    # update soundpath and the marker sound if an audiofolder name is valid
    df = update_soundpath_and_soundmarker(df, audiofolder, datum)
    #print(df[~df['soundpath'].isnull()])
    # print(df.columns.tolist())
    return df
def update_soundpath_and_soundmarker(df, audiofolder, datum):
    if not audiofolderisvalid(audiofolder):
        pass  # do nothing
    else:
        updates = maaktijdslijstaudio(datum, audiofolder)
        # Apply updates
        for update in updates:
            timestamp_start_str = update[0]
            timestamp_stop_str = update[1]
            new_path = update[2]
            timestamp_start = pd.to_datetime(timestamp_start_str)
            df.loc[df['isodatetime'] == timestamp_start, 'soundpath'] = new_path
            timestamp_stop = pd.to_datetime(timestamp_stop_str)
            df.loc[(df['isodatetime'] >= timestamp_start) & (df['isodatetime'] <= timestamp_stop), 'sound'] = 1
    return df
def col_lst_always(str_c_time, str_c_laeq1s):
    """Put the columnames that are always interesting into list"""
    lst = [str_c_time, str_c_laeq1s]
    return lst
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
