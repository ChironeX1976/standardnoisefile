from slm_BenK import b_en_k_2250dataprep_bb, b_en_k_2250dataprep_spec
import pandas as pd
import io
import base64
import chardet
import csv
from std_columns import lstlaeqspellings, check_isoneoflist_inbiglist
def parse_contents(contents, filename):
    """ Decodeert de inhoud en leest de data in als string en maakt er decoded_bytes van.
    Retourneert niks als het geen textbestand is """
    content_type, content_string = contents.split(',')  # Scheid metadata en base64-encoded inhoud
    decoded_bytes = base64.b64decode(content_string)  # Decodeer de base64-string naar bytes
    sample_decoded_bytes = decoded_bytes[:10000]
    enc = read_encoding(sample_decoded_bytes)
    sample_content_string = sample_decoded_bytes.decode(enc)
    delimiterr = read_delimiter(sample_content_string)
    try:
        # Als het een tekstbestand of CSV is
        if filename.endswith('.txt') or filename.endswith('.csv'):
            #text = io.StringIO(decoded.decode('utf-8')).read()
            #print("tekstbestand gedetecteerd")
            return decoded_bytes, enc, delimiterr
        # Als het een afbeelding is
        elif filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            #print("foto gedetecteerd")
            return
        else:
            print (f"Bestand {filename} gedetecteerd, maar geen text of foto, kan niks mee doen.")
            return
    except Exception as e:
        print(f"Fout bij verwerken van bestand {filename}: {str(e)}")
        return


def data_init (contents, filenames):
    ''' Data initialisation
    Check if the inputfile is valid
    If it is valid, then standardize the file and return a dictionary of the dataframe
    :parameter
        contents: string from dcc input component
        filenames: string from dcc input component
    :returns
        geldigheid: string why it is valid or nog
        dict_df: a dictionary of a datframe to store in the dash web page
    '''
    dict_df = dict()
    for c, f in zip(contents, filenames):
        strdecoded, encodingg, delimiterr = parse_contents(c, f)
        if strdecoded is None:
            geldigheid = "niet geldige file"
            return geldigheid
        else:
            # check sonometer type, based on decoded string
            invalid, slmtype = categorize_slm_from_inputdata(strdecoded, f, encodingg, delimiterr)
            if invalid:
                geldigheid = 'niet geldige file'
            else:
                df = data_prep(slmtype, strdecoded, f, encodingg, delimiterr)
                geldigheid = 'geldige file van ' + slmtype
                if len(dict_df) == 0: # if there is nothing in the dfdict variable, then it is the first filename
                    dict_df = df.to_dict('records')
                else: # if there is already something in the dfdict variable, then we try to merge the data
                    df0 = pd.DataFrame(dict_df)
                    df = pd.merge_ordered(df0, df, on = 'time')
                    dict_df = df.to_dict('records')
    return geldigheid, dict_df

def categorize_slm_from_inputdata(decoded, filename, encodingg, delimiterr):
    """Categorise type of sound level meter (slm) - dataset-types,
       by reading the filename and the first 5 lines of the raw dataset (string),
    At the moment only the data from a slm called Bruel and Kjaer-2250 is programmed
     :param
        iostring: string from from a dash core component - upload
        filename
    :returns
        invalid: True when the data source is unknown
        slm: (abbrev, sound level meter) string with the name of the data source or unkown when it is invalid
     """
    lst_typeslmdataset =["Bruel and Kjaer-2250_BB", "Bruel and Kjaer-2250_Spectra", "standardized", "01dB-duo"]
    # read first 5 lines of dataset. the \t is tricky. sometimes it crashes. errorhandling should be programmed later
    df = pd.read_csv(io.StringIO(decoded.decode(encodingg)), delimiter=delimiterr, engine="python", decimal=',')
    if 'loggedbb' in filename.lower():
        # categorize through some standard column-names
        if df.columns[0] == "Project Name" and check_isoneoflist_inbiglist (lstlaeqspellings(), df.columns.tolist()):     # bruel and kjaer - 2250 - broadband file
            slmtype = lst_typeslmdataset[0]
            invalid = False
    elif 'loggedspectra' in filename.lower():
        # categorize through some standard column-names
        if df.columns[0] == "Project Name" and (any("lzeq 1khz" in col.lower() for col in df.columns)):     # bruel and kjaer - 2250 - spectrumfile
            slmtype = lst_typeslmdataset[1]
            invalid = False
    else:
        if df.columns[0] == 'time':           # a file created with this dashboard (based on any type of slm)
            slmtype = lst_typeslmdataset[2]
            invalid = False
        elif df.columns[0] == "Period Start":   # 01dB
            slmtype= lst_typeslmdataset[3]
            invalid = False
        else:                                   # unknown
            slmtype="unknown file"
            invalid = True
    return invalid, slmtype

def data_prep(typeslmdataset:str, decoded:str, filename:str, encodingg, delimiterr):
    if typeslmdataset == "Bruel and Kjaer-2250_BB":
        df = b_en_k_2250dataprep_bb(decoded, filename, encodingg, delimiterr)
    elif typeslmdataset == "Bruel and Kjaer-2250_Spectra":
        df = b_en_k_2250dataprep_spec(decoded, filename,encodingg, delimiterr)

    elif typeslmdataset == "standardized":
        print('bestaat niet')
        # lst_flds_a, lst_flds_st, lst_flds_m_used, begintime, df, lstsound, spectralinfo = standard_dataprep(decoded, filename)
    else:
        print(typeslmdataset, ", not programmed yet")
    return df

def saveas_standard_csv_in_data_dir(dict_df, f):
    #f = 'c:/tmp/std_file.txt'
    df = pd.DataFrame(dict_df)
    df['time'] = pd.to_datetime(df['time'])
    df.to_csv(f, sep="\t", index=False)
    return f"Bestand {f} , data saved"
def read_encoding(bytessample):
    result = chardet.detect(bytessample)
    enc = result['encoding']
    return enc
def read_delimiter(txt):
    sniffer = csv.Sniffer()
#BIJ CSV BESTAND VAN FUSION KAN HIJ NIET DETECTEREN WELKE DELIMITERS ER VAN TOEPASSING ZIJN
    print(txt)
    try:
        dialect = sniffer.sniff(txt)
        delim = dialect.delimiter
    except csv.Error:
        delim = ","
    print ('delimiter', delim)
    return delim