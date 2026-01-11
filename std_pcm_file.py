import pandas as pd
import io
def standard_pcm_file (decodeddata, fileproperties):
    """the standard pcm file is just read and the dataframe is passed through unchanged.
     It will might be merged with another standard file if more than one file is dragged and dropped in the layout"""
    enc = fileproperties['encoding']
    delim = fileproperties['delim']
    skiprows = fileproperties['skiprows']
    # read into pandas dataframe
    df = pd.read_csv(io.StringIO(decodeddata.decode(enc)), delimiter=delim, skiprows=skiprows, engine="python")
    return df