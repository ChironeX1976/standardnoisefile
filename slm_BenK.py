from  std_columns import standardize,  standard_column_names, standardize_spectrumdata, lst_standard_statscolumn_names,lst_standard_spectrumcolumn_names, standardize_statsdata , standardize_minmaxdata
import pandas as pd
import io
import numpy as np
from collections import Counter
import os
def b_en_k_2250dataprep_bb(decodeddata:str,f:str):
    # read into pandas dataframe
    df = pd.read_csv(io.StringIO(decodeddata.decode('utf-8')), delimiter="\t", skiprows=0, engine="python", decimal=',')
    #df = pd.read_csv('C:/Werk/py/datapreparation/testdata/GL 22  007_LoggedBB.txt', delimiter="\t", skiprows=0, engine="python", decimal=',')
    # get standard columnames
    str_c_laeq1s, str_c_time,  str_c_soundpath, str_c_exclude, lst_strminmax = standard_column_names()
    # standardize a few essential column-names of the dataframe
    df = standardize(df, str_c_soundpath, str_c_exclude, str_c_time, str_c_laeq1s)
    # get interesting fields
    lst_flds_a = col_lst_always(str_c_time,str_c_laeq1s)
    # get other interesting columns that are not mandatory
    # statistics columns
    lst_flds_st = [] # no stat fields, empty list
    df, containsstats = standardize_statsdata(df)
    if containsstats: lst_flds_st = lst_standard_statscolumn_names() # statfields in a list
    # min max  columns
    lst_flds_minmax = []  # no minmax fields
    df, containsminmax = standardize_minmaxdata(df)
    if containsminmax: lst_flds_minmax = lst_strminmax  # minmax
    # marker columns
    lst_flds_m_all = b_en_k_fldslst_marker_all(df) # retrieve all marker columns and put in a list
    lst_flds_m_unused = b_en_kfldlst_marker_unused(df,lst_flds_m_all) # which markers ar not used
    lst_flds_m_used = b_enkfldlst_marker_used(lst_flds_m_all,lst_flds_m_unused) # which markers are used indeed
    # selection of all interesting fields in dataframe
    lst_interesting = lst_flds_a + lst_flds_m_used + [str_c_soundpath] + lst_flds_st + lst_flds_minmax
    df = df[lst_interesting]
    df.replace(0, np.nan, inplace=True)
    # create time object
    df[str_c_time] = pd.to_datetime(df[str_c_time], format='%d/%m/%Y %H:%M:%S')
    # use basename of soundpaths if not.na
    df[str_c_soundpath] = df[str_c_soundpath].apply(lambda x: os.path.basename(x) if isinstance(x, str) else None)

    return df
def b_en_k_2250dataprep_spec (decodeddata:str,f:str):
    # read into pandas dataframe
    df = pd.read_csv(io.StringIO(decodeddata.decode('utf-8')), delimiter="\t", skiprows=0, engine="python", decimal=',')
    # get standard columnames
    str_c_laeq1s, str_c_time,  str_c_soundpath, str_c_exclude, lst_strminmax = standard_column_names()
    lst_stndrd_spectrcols = lst_standard_spectrumcolumn_names()  # list of the spectrum-spelling that i choose
     # standardize a few essential column-names of the dataframe
    df = standardize_spectrumdata(df, str_c_time, lst_stndrd_spectrcols)
    # create time object
    df[str_c_time] = pd.to_datetime(df[str_c_time], format='%d/%m/%Y %H:%M:%S')
    return df

def b_en_k_fldslst_marker_all(df):
    """get all fields whith marker data in list
    marker data-value is always 0 or 1 and nothing else
    """
    lst = []
    for c in df.columns.tolist():
        if df[c].isin([0, 1]).all():
             lst.append(c)
    return lst
def b_en_kfldlst_marker_unused(df,lst):
    """from a list of markerfields -> get those who are unused
    (where all values in the column are equal to 0)
    exception: exclude marker field must always be kept
    """
    lst_unused = []
    for l in lst:
        if df[l].isin([0]).all():
            if l not in ["Exclude", 'exclude']: # exclude must always be "useable" -  even if it is not yet used
                lst_unused.append(l)
    return lst_unused
def b_enkfldlst_marker_used(lstall, lstunused):
    """ substract two lists of strings:
    all markers minus the unused markers equals the used markers
    """
    c1 = Counter(lstall)
    c2 = Counter(lstunused)
    diff = c1 - c2
    return list(diff.elements())
def col_lst_always(str_c_time, str_c_laeq1s):
    """Put the columnames that are always interesting into list"""
    lst = [str_c_time, str_c_laeq1s]
    return lst
def b_en_k_fldslst_stats():
    """Put statistical fields, that are always interesting, into list"""
    lst = ['LAF1,0', 'LAF5,0', 'LAF10,0', 'LAF50,0', 'LAF90,0', 'LAF95,0', 'LAF99,0']
    return lst


# b_en_k_2250dataprep_bb()