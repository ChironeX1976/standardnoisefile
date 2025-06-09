import chardet
import pandas as pd
import csv
import io

import base64
import mimetypes
import os

from slm_01db import zero1db_dataprep

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


def read_encoding(bytessample):
    result = chardet.detect(bytessample)
    enc = result['encoding'] or 'utf-8'
    print('encoding:', enc)
    return enc

def detect_delimiter(sample_text):
    try:
        # sample_for_sniffer = filter_valid_lines(sample_text, skiprows)
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample_text)
        delim = dialect.delimiter
        msg = "TAB" if delim == '\t' else delim
        return delim, msg
    except Exception as e:
        print(f"[DEBUG] Fout bij detecteren delimiter: {e}")
        return ',', 'fallback (default ,)'
def evaluate_first_line(sample_text):
    """
    Evaluates the first line of the sample text.
    Returns:
        skiprows (int): 1 if 'fusion' is in the first line,
                        0 if 'Project Name' is in the first line,
                        defaults to 0 otherwise.
    """
    first_line = sample_text.splitlines()[0].lower()

    if 'fusion' in first_line:
        return 1,'fusion'
    elif 'project name' in first_line:
        if 'laeq' in first_line:
            return 0, 'benk_bb'
        if 'lzeq 500hz' in first_line:
            return 0, 'benk_spectra'
    else:
        return 0,'unknown source'

# f1 = 'testdata/GL75-050_LoggedSpectra.txt'
# f2 = 'testdata/GL75-050_LoggedBB.txt'
f3 = 'testdata/01.csv'
# f4 = 'testdata/dummy_file_nodata.txt'
contents, filename  = simulate_dash_upload(f3)
content_type, content_string = contents.split(',')
# main logic
decoded = base64.b64decode(content_string)

# first read the encoding
enc = read_encoding(decoded[:1024])

# try to make a sample string
try:
    sample_lines = decoded.decode(enc).splitlines()
    sample = '\n'.join(sample_lines[:30])  # or however many lines you want
except UnicodeDecodeError:
    sample = decoded.decode('utf-8', errors='ignore')


# Evaluate only the first line
skiprows, source = evaluate_first_line(sample)
print("Skiprows based on first line:", skiprows, "sourcefile:",source)
#
delim, msg = detect_delimiter(sample)
print('delim:', delim, msg)

zero1db_dataprep(decoded, enc, delim,skiprows)
#
# try:
#      df = pd.read_csv(io.StringIO(sample), delimiter=delim, skiprows=skiprows)
#      print(df.head())
# except Exception as e:
#      print("[FOUT bij pandas.read_csv]:", e)


