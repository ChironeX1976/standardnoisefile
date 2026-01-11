import pandas as pd
import numpy as np
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

    # kompas-waarden volgens vlarem 2 bijlage 4.5.1 artikel 4§2
    wind_dict = get_wind_compass_definitions(df['winddir_degrees'])

    # np.select verwacht nog steeds twee lijsten, maar die halen we nu veilig uit de dict:
    df['winddir_compass'] = np.select(
        list(wind_dict.values()),  # De condities
        list(wind_dict.keys()),  # De namen (N, NO, etc.)
        default='VAR'
    )



    # Filter and print the rows
    #filtered_df = df[df['exclude_meteo'] == 1]
    #print(filtered_df)
    print(df)
    return df


def get_wind_compass_definitions(series):
    """
    Geeft een dictionary terug met windstreek-definities.
    Sleutels zijn de windstreken, waarden zijn de bijbehorende condities.
    """
    # We gebruiken een dictionary om de koppeling expliciet te maken
    definitions = {
        'N':  (series >= 337.5) | (series <= 22.5),
        'NO': (series > 22.5)   & (series < 67.5),
        'O':  (series >= 67.5)  & (series <= 112.5),
        'ZO': (series > 112.5)  & (series < 157.5),
        'Z':  (series >= 157.5) & (series <= 202.5),
        'ZW': (series > 202.5)  & (series < 247.5),
        'W':  (series >= 247.5) & (series <= 292.5),
        'NW': (series > 292.5)  & (series < 337.5)
    }
    return definitions