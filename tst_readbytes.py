import chardet
import pandas as pd
import csv
import io
import base64
import mimetypes
import os
from slm_01db import zero1db_dataprep
from slm_BenK import b_en_k_2250dataprep_bb, b_en_k_2250dataprep_spec


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
        # sample_for_sniffer = filter_valid_lines(sample_text, skiprows)
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample_text)
        delim = dialect.delimiter
        msg = "TAB" if delim == '\t' else delim
        print(msg)
        return delim
    except Exception as e:
        print(f"[DEBUG] Fout bij detecteren delimiter: {e}")
        return ',', 'fallback (default ,)'
def get_slmtype(sample_text):
    """
    Evaluates the first line of the sample text of a dataset.
    Returns:
        invalid:default = True
        skiprows (int): 1 if 'fusion' is in the first line,
                        0 if 'Project Name' is in the first line,
                        defaults to 0 otherwise.
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
    else:
        slmtype = "unknown slm file"
    return invalid, slmtype
def get_rowstoskip(slmtype):
    if slmtype == 'fusion':
        skiprows = 1
    else:
        skiprows = 0
    return skiprows
def parse_contents(contents, filename):
    """ Decodeert de inhoud en leest de data in als string en maakt er decoded_bytes van.
        Retourneert niks als het geen textbestand is """
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        # Als het een tekstbestand of CSV is
        if filename.endswith('.txt') or filename.endswith('.csv'):
            # text = io.StringIO(decoded.decode('utf-8')).read()
            # print("tekstbestand gedetecteerd")
            return decoded
        # Als het een afbeelding is
        elif filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            # print("foto gedetecteerd")
            return
        elif filename.endswith(('.mp3')):
            print(f"audiobestand {filename}" )
            return
        else:
            print(f"Bestand {filename} gedetecteerd, maar geen text of foto, kan niks mee doen.")
            return
    except Exception as e:
        print(f"Fout bij verwerken van bestand {filename}: {str(e)}")
        return
    return
def data_init (contents, filenames, audiofolder):
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
                df = data_prep(strdecoded, fileproperties, audiofolder)
                geldigheid = 'geldige file van ' + fileproperties['slmtype']
                if len(dict_df) == 0: # if there is nothing in the dfdict variable, then it is the first filename
                    dict_df = df.to_dict('records')
                else: # if there is already something in the dfdict variable, then we try to merge the data
                    df0 = pd.DataFrame(dict_df)
                    df = pd.merge_ordered(df0, df, on = 'time')
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
    # make a small sample of the data
    sample = make_datasample(decoded,enc)
    # get type of sound level meter (slm)
    invalid, slmtype = get_slmtype(sample)
    # detect the delimiters in the sample
    delim = get_delimiter(sample)
    # get rows to skip in the dataset
    skiprows=get_rowstoskip(slmtype)
    values =[filename, enc, invalid, slmtype, delim, skiprows]
    properties=dict(zip(keys,values))
    return properties
def data_prep(decoded:str, fileproperties, audiofolder):
    slmtype = fileproperties['slmtype']
    if slmtype == "benk_bb":
        print ('benk_bb')
        df = b_en_k_2250dataprep_bb(decoded, fileproperties)
    elif slmtype == "benk_spectra":
        print('benkspectra')
        df = b_en_k_2250dataprep_spec(decoded, fileproperties)
    elif slmtype == "fusion":
        df = zero1db_dataprep(decoded, fileproperties, audiofolder)
    elif slmtype  == "standardized":
        print('detectie op gestandardizeerde file bestaat niet')
    else:
        print(slmtype, ", not programmed yet")
    return df

# f1 = 'testdata/GL75-050_LoggedSpectra.txt'
f2 = 'testdata/GL75-050_LoggedBB.txt'
f3 = 'testdata/01.csv'
f4 = 'testdata/dummy_file_nodata.txt'
f5 = 'testdata/GL 22  007_LoggedBB.txt'
f6= 'testdata/audio/01db/080945_080954.mp3'
lst =['testdata/audio/01db/080945_080954.mp3','testdata/01.csv', 'testdata/audio/01db/081001_081010.mp3' ]

audiofolder="c:/tmp"
contents, filename  = simulate_dash_upload(f3)
if not isinstance(contents, list):
    contents = [contents]
    filename = [filename]
geldigheid, dict_df = data_init(contents, filename, audiofolder)
print(geldigheid)

