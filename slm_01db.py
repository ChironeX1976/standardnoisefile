import pandas as pd
from  std_columns import standardize,  standard_column_names, standardize_spectrumdata, lst_standard_statscolumn_names,lst_standard_spectrumcolumn_names, standardize_statsdata , standardize_minmaxdata

import io

def zero1db_dataprep(decodeddata:str, enc, delim,skiprows):
    df = pd.read_csv(io.StringIO(decodeddata.decode(enc)), delimiter=delim, skiprows=skiprows, skipfooter = 96, engine="python", decimal=',')
    # get standard columnames
    str_c_laeq1s, str_c_time, str_c_soundpath, str_c_exclude, lst_strminmax = standard_column_names()
    # standardize a few essential column-names of the dataframe
    df = standardize(df, str_c_soundpath, str_c_exclude, str_c_time, str_c_laeq1s)
    # get interesting fields
    lst_flds_a = col_lst_always(str_c_time, str_c_laeq1s)
    # min max  columns
    lst_flds_minmax = []  # no minmax fields
    df, containsminmax = standardize_minmaxdata(df)
    if containsminmax: lst_flds_minmax = lst_strminmax  # minmax

    lst_interesting = lst_flds_a + lst_flds_minmax
    df = df[lst_interesting]
    #spectrumcolumns
    print(df.columns.tolist())
    return df

def col_lst_always(str_c_time, str_c_laeq1s):
    """Put the columnames that are always interesting into list"""
    lst = [str_c_time, str_c_laeq1s]
    return lst