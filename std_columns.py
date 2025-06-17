# from tarfile import data_filter
def standard_column_names():
    """returns standard column names"""
    str_c_laeq1s ="laeq1s" #column name with laeq1s
    str_c_time = "isodatetime" # column name with time stamp
    str_c_soundpath = "soundpath"
    str_c_exclude = "exclude"
    lst_c_minmax = ['lafmin','lafmax']
    return str_c_laeq1s, str_c_time,  str_c_soundpath,str_c_exclude, lst_c_minmax
def lst_standard_statscolumn_names():
    """returns standard column names of statistics"""
    lst = lst_stats_spellings()[3]
    return lst
def lst_standard_minmaxcolumn_names():
    """returns standard column of min en max"""
    lst = lst_minmax_spellings()[2]
    return lst
def lst_standard_spectrumcolumn_names():
    """returns standard column names of spectra"""
    lst = lst_spectra_spellings()[3]
    return lst
def lstlaeqspellings():
    lst = ['LAeq', 'lAeq', 'LAEQ1S', 'LAeq1s', 'laeq1s']
    return lst
def standardize(df, str_c_soundpath, str_c_exclude, str_c_time,str_c_laeq1s):
    """Although the same instrument, sometimes different column names are used in exportdata from the device.
    Here, standards are introduced as the file is read.
    :parameter
        df: dataframe
        str_c_soundpath: string in which the sound path is stored"""
    for c in df.columns.tolist():
        if c in lstlaeqspellings():
            df.rename(columns={c:str_c_laeq1s}, inplace=True)
        if c in ['Start Time', 'starttime', 'Start time', 'start Time']:
            df.rename(columns={c:str_c_time}, inplace=True)
        if c in ['Sound Path', 'sound Path', 'soundpath', 'SoundPath', 'sound path']:
            df.rename(columns={c:str_c_soundpath}, inplace=True)
        if c in ['Exclude', 'exclude', 'exc']:
            df.rename(columns={c: str_c_exclude}, inplace=True)
    return df #with the standard columnames
def standardize_spectrumdata(df, str_c_time, lst_stndrd_spectrcols):
    """change the columnames in dataframe to a standard choice"""
    # loop through columns of df (spectrum data)
    for c in df.columns.tolist():
        # rename column time in standard columname
        if c in ['Start Time', 'starttime', 'Start time', 'start Time']:
            df.rename(columns={c: str_c_time}, inplace=True)
        # rename frequencies in standard columname
        for lst_sp in lst_spectra_spellings():
            if c in lst_sp:
                freqindx = (lst_sp.index(c)) # get index of columname that is found
                # rename with corresponding index from the standard column-names
                df.rename(columns={c: lst_stndrd_spectrcols[freqindx]}, inplace=True)
    lst_cols_keep = [str_c_time]
    lst_cols_keep.extend(lst_stndrd_spectrcols)
    df= df[lst_cols_keep]
    return df
def standardize_minmaxdata(df):
    """change the columnames in dataframe to a standard choice, if no statistics columns are found,
        the same dataframe is returned and a False statement"""
    df_contains_minmax = False
    for c in df.columns.tolist():
        for lst_minmax in lst_minmax_spellings():
            if c in lst_minmax:
                indx = lst_minmax.index(c)
                df.rename(columns={c: lst_standard_minmaxcolumn_names()[indx]}, inplace=True)
                df_contains_minmax = True
    return df, df_contains_minmax
def standardize_statsdata(df):
    """change the columnames in dataframe to a standard choice, if no statistics columns are found,
    the same dataframe is returned and a False statement"""
    df_contains_stats = False
    for c in df.columns.tolist():
        for lst_stat in lst_stats_spellings():
            if c in lst_stat:
                indx = lst_stat.index(c)
                df.rename(columns={c:lst_standard_statscolumn_names()[indx]}, inplace=True)
                df_contains_stats = True
    return df, df_contains_stats
def lst_minmax_spellings():
    """Even when the same brand of sound level meter is used, the column-names for min max
            that it spits out can differ.
            Here is a list of all the spellings that i found"""
    lst = (['LAFmin', 'LAFmax'], ['LAFMIN','LAFMAX'], ['lafmin','lafmax'],['LAFMax','LAFMin'])
    return lst
def lst_stats_spellings():
    """Even when the same brand of sound level meter is used, the column-names for statistiscs
        that it spits out can differ.
        Here is a list of all the spellings that i found"""
    lst= (["LA1", "LA5", "LA10", "LA50", "LA90", "LA95", "LA99"],
          ["LAF1", "LAF5", "LAF10", "LAF50", "LAF90", "LAF95", "LAF99"],
          ["LAF1,0","LAF5,0","LAF10,0","LAF50,0","LAF90,0","LAF95,0","LAF99,0"],
          ["la1","la5","la10","la50","la90","la95","la99"])
    return lst
def lst_spectra_spellings():
    """Even when the same brand of sound level meter is used, the column-names for terts-band frequencies
    that it spits out can differ.
    Here is a list of all the spellings that i found
    I am not interested in lower than 25 Hz and higher than 20 kHz"""
    lst = ['LZeq25Hz', 'LZeq31.5Hz', 'LZeq40Hz', 'LZeq50Hz', 'LZeq63Hz', 'LZeq80Hz', 'LZeq100Hz',
                 'LZeq125Hz', 'LZeq160Hz', 'LZeq200Hz', 'LZeq250Hz', 'LZeq315Hz', 'LZeq400Hz', 'LZeq500Hz',
                 'LZeq630Hz', 'LZeq800Hz', 'LZeq1kHz', 'LZeq1.25kHz', 'LZeq1.6kHz', 'LZeq2kHz', 'LZeq2.5kHz',
                 'LZeq3.15kHz', 'LZeq4kHz', 'LZeq5kHz', 'LZeq6.3kHz', 'LZeq8kHz', 'LZeq10kHz', 'LZeq12.5kHz',
                 'LZeq16kHz', 'LZeq20kHz'],\
          ['LZeq25Hz', 'LZeq31.5Hz', 'LZeq40Hz', 'LZeq50Hz', 'LZeq63Hz', 'LZeq80Hz', 'LZeq100Hz',
                 'LZeq125Hz', 'LZeq160Hz', 'LZeq200Hz', 'LZeq250Hz', 'LZeq315Hz', 'LZeq400Hz', 'LZeq500Hz',
                 'LZeq630Hz', 'LZeq800Hz', 'LZeq1000Hz', 'LZeq1250Hz', 'LZeq1600Hz', 'LZeq2000Hz', 'LZeq2500Hz',
                 'LZeq3150Hz', 'LZeq4000Hz', 'LZeq5000Hz', 'LZeq6300Hz', 'LZeq8000Hz', 'LZeq10000Hz', 'LZeq12500Hz',
                 'LZeq16000Hz', 'LZeq20000Hz'],\
          ['LZeq 25Hz', 'LZeq 31.5Hz', 'LZeq 40Hz', 'LZeq 50Hz', 'LZeq 63Hz', 'LZeq 80Hz', 'LZeq 100Hz',
                 'LZeq 125Hz', 'LZeq 160Hz', 'LZeq 200Hz', 'LZeq 250Hz', 'LZeq 315Hz', 'LZeq 400Hz', 'LZeq 500Hz',
                 'LZeq 630Hz', 'LZeq 800Hz', 'LZeq 1kHz', 'LZeq 1.25kHz', 'LZeq 1.6kHz', 'LZeq 2kHz', 'LZeq 2.5kHz',
                 'LZeq 3.15kHz', 'LZeq 4kHz', 'LZeq 5kHz', 'LZeq 6.3kHz', 'LZeq 8kHz', 'LZeq 10kHz', 'LZeq 12.5kHz',
                 'LZeq 16kHz', 'LZeq 20kHz'],\
          ['lzeq25hz', 'lzeq31.5hz', 'lzeq40hz', 'lzeq50hz', 'lzeq63hz', 'lzeq80hz', 'lzeq100hz',
                 'lzeq125hz', 'lzeq160hz', 'lzeq200hz', 'lzeq250hz', 'lzeq315hz', 'lzeq400hz', 'lzeq500hz',
                 'lzeq630hz', 'lzeq800hz', 'lzeq1khz', 'lzeq1.25khz', 'lzeq1.6khz', 'lzeq2khz', 'lzeq2.5khz',
                 'lzeq3.15khz', 'lzeq4khz', 'lzeq5khz', 'lzeq6.3khz', 'lzeq8khz', 'lzeq10khz', 'lzeq12.5khz',
                 'lzeq16khz', 'lzeq20khz'], \
          ['lzeq25', 'lzeq31.5', 'lzeq40', 'lzeq50', 'lzeq63', 'lzeq80', 'lzeq100',
           'lzeq125', 'lzeq160', 'lzeq200', 'lzeq250', 'lzeq315', 'lzeq400', 'lzeq500',
           'lzeq630', 'lzeq800', 'lzeq1000', 'lzeq1250', 'lzeq1600', 'lzeq2000', 'lzeq2500',
           'lzeq3150', 'lzeq4000', 'lzeq5000', 'lzeq6300', 'lzeq8000', 'lzeq10000', 'lzeq12500',
           'lzeq16000', 'lzeq20000'], \
          ['25', '31.5', '40', '50', '63', '80', '100', '125', '160', '200', '250', '315', '400', '500',
           '630', '800', '1000', '1250', '1600', '2000', '2500', '3150', '4000', '5000', '6300', '8000', '10000', '12500',
           '16000', '20000'], \
          ['25', '31.5', '40', '50', '63', '80', '100', '125', '160', '200', '250', '315', '400', '500',
           '630', '800', '1k', '1.25k', '1.6k', '2k', '2.5k', '3.15k', '4k', '5k', '6.3k', '8k', '10k',
           '12.5k','16k', '20k'], \
          [25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500,
           630, 800, 1000, 1250, 1600, 2000, 2500,3150, 4000,5000, 6300, 8000, 10000, 12500,
           16000, 20000],\
        ['25 Hz', '31.5 Hz', '40 Hz', '50 Hz', '63 Hz', '80 Hz', '100 Hz', '125 Hz', '160 Hz', '200 Hz', '250 Hz', '315 Hz',
        '400 Hz', '500 Hz', '630 Hz', '800 Hz', '1 kHz', '1.25 kHz', '1.6 kHz', '2 kHz', '2.5 kHz', '3.15 kHz', '4 kHz',
        '5 kHz', '6.3 kHz', '8 kHz', '10 kHz', '12.5 kHz', '16 kHz', '20 kHz', ]
    return lst
def check_isoneoflist_inbiglist (checklist, biglist):
    "checks if one checkitem of a checkitemlist is within a biglist, and turns true or false"
    if any(checkitem in biglist for checkitem in checklist):
        check_isoneoflist_inbiglist = True
    else:
        check_isoneoflist_inbiglist = False
    return check_isoneoflist_inbiglist
def col_lst_always(str_c_time, str_c_laeq1s):
    """Put the columnames that are always interesting into list"""
    lst = [str_c_time, str_c_laeq1s]
    return lst

# def drop_last_non_unique_column(df):
#     """
#     Drops the last column with a non-unique name in the DataFrame.
#
#     Parameters:
#         df (pd.DataFrame): The input DataFrame.
#
#     Returns:
#         pd.DataFrame: A new DataFrame with the last non-unique column removed.
#     """
#     cols = df.columns
#     non_unique_indices = [i for i, col in enumerate(cols)
#                           if list(cols).count(col) > 1]
#
#     if non_unique_indices:
#         last_non_unique_idx = max(non_unique_indices)
#         return df.drop(df.columns[last_non_unique_idx], axis=1)
#
#     # Return original if no non-unique column names exist
#     return df
