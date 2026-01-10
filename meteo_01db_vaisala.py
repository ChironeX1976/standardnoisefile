import numpy as np
import pandas as pd
from io import BytesIO
def meteo_01dB_vaisala_dataprep(decoded,fileproperties):
    # read dataset
    df = pd.read_excel(BytesIO(decoded), skiprows = fileproperties['skiprows'])
    # Define the mapping of old names to new names
    mapping = {'Data type' : 'isodatetime',
        'Wind speed': 'wind_m/s',
        'Wind direction': 'winddir_degrees',
        'Rain intensity': 'rain_mm/h'
    }

    # Apply the rename
    df = df.rename(columns=mapping)

    # Keep all rows starting from index 2 to the end
    df = df.iloc[2:].reset_index(drop=True)
    df = df.iloc[:-1].reset_index(drop=True)
    df['wind_invalid'] = df['wind_m/s'] > 4.9
    df['rain_invalid'] = df['rain_mm/h'] > 0
    # Create 'exclude_meteo' as 1 if either invalid column is True, else 0
    df['exclude_meteo'] = (df['wind_invalid'] | df['rain_invalid']).astype(int)

    # Filter and print the rows
    filtered_df = df[df['exclude_meteo'] == 1]
    print(filtered_df)
    print(df)
    return df