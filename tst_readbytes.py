import chardet
import pandas as pd
import csv

f1 = 'testdata/GL75-050_LoggedBB.txt'
f2 = 'testdata/01.csv'
numberofbytes = 10000
def read_encoding(f):
    with open(f, 'rb') as f:
        result = chardet.detect(f.read(numberofbytes))  # leest 10 KB
    return result['encoding']
def check_encoding_and_delimiters(f):
    enc = read_encoding(f)
    with open(f,'r', encoding=enc) as f:
        sample = f.read (numberofbytes)
        sniffer = csv.Sniffer()
        try:
            dialect = sniffer.sniff(sample)
            delimiter = dialect.delimiter
        except csv.Error:
            delimiter = ","
    return enc, delimiter


print(check_encoding_and_delimiters(f1))
print (check_encoding_and_delimiters(f2))

# df2= pd.read_csv('testdata/GL75-050_LoggedBB.txt', delimiter = "\t", encoding=result['encoding'])
# #pd.read_csv('testdata/GL75-050_LoggedBB.txt', delimiter="\t", engine="python", decimal=',')
# print(df2)