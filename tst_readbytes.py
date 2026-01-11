import base64
import chardet
import csv
import pandas as pd
import mimetypes
import os
from io import BytesIO
import openpyxl
from slm_01db import zero1db_dataprep
from slm_BenK import b_en_k_2250dataprep_bb, b_en_k_2250dataprep_spec
from slm_svantek import svantek_dataprep
from slm_norsonicxlsx import norsonic140xlsx_dataprep
from meteo_01db_vaisala import meteo_01dB_vaisala_dataprep
from std_pcm_file import standard_pcm_file
from std_columns import standard_column_names

"""THIS FILE IS ONLY FOR TESTING PURPOSES"""

def simulate_dash_upload(file_path):
    # Read the file in binary mode
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
    # Guess the MIME type from file extension
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = 'text/plain'  # default fallback
    # Base64 encode the content
    base64_content = base64.b64encode(file_bytes).decode('utf-8')
    # Construct the same string as dcc.Upload would provide
    contents = f"data:{mime_type};base64,{base64_content}"
    filename = os.path.basename(file_path)
    return contents, filename
def get_encoding(bytessample):
    result = chardet.detect(bytessample)
    enc = result['encoding'] or 'utf-8'
    print('encoding:', enc)
    return enc
def get_delimiter(sample_text):
    try:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample_text)
        delim = dialect.delimiter
        msg = "TAB" if delim == '\t' else delim
        print('delimiter:', msg)
        return delim
    except Exception as e:
        print(f"[DEBUG] Fout bij detecteren delimiter: {e}")
        return ',', 'fallback (default ,)'
def get_slmtypexlsx(decoded):
    """
        Evaluates a .xlsx - dataset
        Returns:
            invalid:default = True
            slmtype =  string with name of source
        """
    invalid = True
    excel_file = pd.ExcelFile(BytesIO(decoded))
    try:
        # Retrieve the list of sheet names
        sheet_names_list = excel_file.sheet_names
        if "Summary" in sheet_names_list:
            slmtype = "norsonic140"
            invalid = False
        else:
            #1. Get the name of the first sheet
            first_sheet = excel_file.sheet_names[0]
            df_headers = pd.read_excel(excel_file, sheet_name=0, nrows=0)
            lst_headers = (df_headers.columns.tolist())

            # Check if 'cmg' is in ANY element AND 'File' is in ANY element
            has_cmg = any('cmg' in item for item in lst_headers)
            has_file = any('File' in item for item in lst_headers)

            if has_cmg and has_file:
                print("This is a file from 01dB - dbTrait - further investigation...")
                df_headers = pd.read_excel(excel_file, sheet_name=0, skiprows=5, nrows=0)
                lst_headers = (df_headers.columns.tolist())
                # Check if 'cmg' is in ANY element AND 'File' is in ANY element
                has_Windspeed = any('Wind speed' in item for item in lst_headers)
                has_Winddir = any('Wind direction' in item for item in lst_headers)
                has_Rain = any('Rain intensity' in item for item in lst_headers)
                if has_Windspeed and has_Winddir and has_Rain:
                    print("... meteo file from a Vaisala WXT520")
                    slmtype = "01dBmeteo"
                    invalid = False

    except Exception as e:
        print(f"An error occurred: {e}")

    return invalid, slmtype
def get_slmtype(sample_text):
    """
    Evaluates the first line of the sample text of a dataset.
    Returns:
        invalid:default = True
        slmtype =  string with name of source
    """
    invalid = True
    first_line = sample_text.splitlines()[0].lower()
    if 'fusion' in first_line:
        invalid = False
        slmtype = 'fusion'
    elif 'project name' in first_line:
        invalid = False
        if 'laeq' in first_line:
            slmtype = 'benk_bb'
        if 'lzeq 500hz' in first_line:
            slmtype = 'benk_spectra'
    elif '// ascii view for the file' in first_line:
        invalid = False
        slmtype ='svantek'
    elif 'isodatetime' in first_line:
            slmtype = 'standard_pcm_file'
            invalid = False
    else:
        slmtype = "unknown slm file"
    return invalid, slmtype
def get_rowstoskip(slmtype):
    if slmtype == 'fusion':
        skiprows = 1
    elif slmtype == 'svantek':
        skiprows = 3
    elif slmtype =='norsonic140':
        skiprows = 2
    elif slmtype == '01dBmeteo':
        skiprows = 5
    else:
        skiprows = 0
    return skiprows
def parse_contents(contents, filename):
    """ Decodeert de inhoud en leest de data in als string en maakt er decoded_bytes van.
        Retourneert niks als het geen textbestand is """
    content_type, content_string = contents.split(',')

    try:
        # Als het een tekstbestand of CSV is
        if filename.endswith('.txt') or filename.endswith('.csv'):
            # text = io.StringIO(decoded.decode('utf-8')).read()
            # print("tekstbestand gedetecteerd")
            decoded = base64.b64decode(content_string)
            return decoded
        # Als het een afbeelding is
        elif filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            # print("foto gedetecteerd")
            return
        elif  filename.endswith('.xlsx'):
            #do something specific with BytesIO
            decoded = base64.b64decode(content_string)

            return decoded
        elif filename.endswith(('.mp3')):
            print(f"audiobestand {filename}" )
            return
        else:
            print(f"Bestand {filename} gedetecteerd, maar geen text of foto, kan niks mee doen.")
            return
    except Exception as e:
        print(f"Fout bij verwerken van bestand {filename}: {str(e)}")
        return

def data_init (contents, filenames, lstaudiofiles):
    ''' Data initialisation
    Check if the inputfile is valid
    If it is valid, then standardize the file and return a dictionary of the dataframe
    :parameter
        contents: string from dcc input component
        filenames: string from dcc input component
    :returns
        geldigheid: string why it is valid or not
        dict_df: a dictionary of a dataframe to store in the dash web page
    '''
    dict_df = dict()
    str_c_laeq1s, str_c_time, str_c_soundpath, str_c_exclude, lst_c_minmax = standard_column_names()
    for c, f in zip(contents, filenames):
        strdecoded = parse_contents(c, f)
        if strdecoded is None:
            geldigheid = "niet geldige file"
            return geldigheid, dict_df
        else:
            # check sonometer type, based on decoded string
            fileproperties = get_fileproperties(strdecoded, f)
            if fileproperties['invalid'] == True:
                geldigheid = 'niet geldige file'
            else:
                df = data_prep(strdecoded, fileproperties, lstaudiofiles)
                geldigheid = 'geldige file van ' + fileproperties['slmtype']
                if len(dict_df) == 0: # if there is nothing in the dfdict variable, then it is the first filename
                    dict_df = df.to_dict('records')
                else: # if there is already something in the dfdict variable, then we try to merge the data
                    df0 = pd.DataFrame(dict_df)
                    df = pd.merge_ordered(df0, df, on = str_c_time)
                    dict_df = df.to_dict('records')
    return geldigheid, dict_df
def make_datasample(decoded, enc):
    # try to make a sample string
    try:
        sample_lines = decoded.decode(enc).splitlines()
        sample = '\n'.join(sample_lines[:30])  # or however many lines you want
    except UnicodeDecodeError:
        sample = decoded.decode('utf-8', errors='ignore')
    return sample
def get_fileproperties(decoded, filename):
    keys = ['filename', 'encoding', 'invalid', 'slmtype', 'delim', 'skiprows']
    # read the encoding
    enc = get_encoding(decoded[:1024])
    if filename.endswith('.xlsx'):
        delim = "dummyexceldelimiter"
        # get type of sound level meter (slm)
        invalid, slmtype = get_slmtypexlsx(decoded)
        skiprows = get_rowstoskip(slmtype)
    else:
        # make a small sample of the data
        sample = make_datasample(decoded, enc)
        # detect the delimiters in the sample
        delim = get_delimiter(sample)
        # get type of sound level meter (slm)
        invalid, slmtype = get_slmtype(sample)
        # get rows to skip in the dataset
        skiprows = get_rowstoskip(slmtype)
    values =[filename, enc, invalid, slmtype, delim, skiprows]
    properties=dict(zip(keys,values))
    return properties
def data_prep(decoded:str, fileproperties, lstaudiofiles):
    slmtype = fileproperties['slmtype']
    if slmtype == "benk_bb":
        df = b_en_k_2250dataprep_bb(decoded, fileproperties)
    elif slmtype == "benk_spectra":
        df = b_en_k_2250dataprep_spec(decoded, fileproperties)
    elif slmtype == "fusion":
        df = zero1db_dataprep(decoded, fileproperties, lstaudiofiles)
    elif slmtype == "svantek":
        df = svantek_dataprep(decoded, fileproperties, lstaudiofiles)
    elif slmtype == "norsonic140":
        df = norsonic140xlsx_dataprep(decoded, fileproperties,lstaudiofiles)
    elif slmtype =="01dBmeteo":
        df = meteo_01dB_vaisala_dataprep(decoded,fileproperties)
    elif slmtype =="standard_pcm_file":
        df = standard_pcm_file (decoded, fileproperties)
    else:
        print(slmtype, ", not programmed yet")
    return df

# f1 = 'testdata/GL75-050_LoggedSpectra.txt'
#f2 = 'testdata/GL75-050_LoggedBB.txt'
#f3 = 'testdata/01db/01.csv'
#f4 = 'testdata/dummy_file_nodata.txt'
#f5 = 'testdata/GL 22  007_LoggedBB.txt'
#f6= 'testdata/audio/01db/080945_080954.mp3'
#f7 = 'testdata/Svan/svan02/L14_noblockoffsetwithcomments.csv'
#f7 = 'testdata/Svan/svan01/L16.csv'
#f8 = 'testdata/Nor140/NOR140_FILE_110412_0003_PROFILE.xlsx'
#f9 = 'testdata/01db/02_meteo.xlsx'
f10 = 'testdata/01db/02_std01db_meteo.txt'
lst =[]

#audiofolder="testdata/Nor140/Recordings_NOR140_FILE_110412_0003"
contents, filename  = simulate_dash_upload(f10)
if not isinstance(contents, list):
    contents = [contents]
    filename = [filename]
geldigheid, dict_df = data_init(contents, filename, lst)
print(geldigheid)

