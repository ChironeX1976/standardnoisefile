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
    df[str_c_soundpath] = np.nan
    lst_interesting = lst_flds_a + lst_flds_minmax + lst_standaardspectrumkolomnamen + [str_c_soundpath]
    df = df[lst_interesting]
    # update audio if a folder name is given and it exists
    if not audiofolderisvalid(audiofolder):
        pass # do nothing
    else:
        updates = maaktijdslijstaudio(datum, audiofolder)
        # Apply updates
        for timestamp_str, new_path in updates.items():
            timestamp = pd.to_datetime(timestamp_str)
            df.loc[df['isodatetime'] == timestamp, 'soundpath'] = new_path
    #print(df[~df['soundpath'].isnull()])
    print(df.columns.tolist())
    return df

def col_lst_always(str_c_time, str_c_laeq1s):
    """Put the columnames that are always interesting into list"""
    lst = [str_c_time, str_c_laeq1s]
    return lst
def maaklijstaudio(folderpth):
    lst_mp3 =[]
    for file in os.listdir(folderpth):
        if file.lower().endswith('.mp3'):
            lst_mp3.append(file)
    return lst_mp3
def maaktijdslijstaudio(datum, folderpth):
    lst_mp3=maaklijstaudio(folderpth)
    lst_isodatetime=[]
    for mp3 in lst_mp3:
        timed = mp3[0:6]
        format = '%H%M%S'
        timed = datetime.strptime(timed, format).time()
        isodatetime = datetime.combine(datum,timed )
        lst_isodatetime.append(isodatetime)
    return dict(zip(lst_isodatetime,lst_mp3))
def audiofolderisvalid(audiofolder):
    folderisvalid = False
    if audiofolder == "":
        return folderisvalid
    if os.path.isdir(audiofolder):
        folderisvalid = True
    return folderisvalid
