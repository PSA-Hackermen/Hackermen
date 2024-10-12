from constants import MARITIME_POINTS
import pandas as pd
import urllib
import json as j
import dotenv

def findRoute(source_dock, dest_dock):

    merged_df = pd.DataFrame()
    for coordinates in MARITIME_POINTS.values():
        lat, long = coordinates 
        df = callAPI(lat, long)
        if merged_df.empty: merged_df = df
        else: merged_df = pd.concat([merged_df, df], ignore_index=True)

    return merged_df

def callAPI(mt_lat, mt_long):
    values = dotenv.dotenv_values(".env")
    request = urllib.request.urlopen(f'https://data.api.xweather.com/maritime/{mt_lat},{mt_long}?filter=1hr&client_id={values["CLIENT_ID"]}&client_secret={values["CLIENT_SECRET"]}')
    response = request.read()
    json = j.loads(response)
    
    if json['success']:
        # Initialize a list to hold extracted data for all periods
        data_list = []

        # Extract latitude and longitude
        location = json['response'][0]['loc']
        lat = location['lat']
        long = location['long']

        # Iterate through all periods and extract relevant data
        for period in json['response'][0]['periods']:
            extracted_data = {
                "dateTimeISO": period['dateTimeISO'],
                "seaSurfaceTemperatureC": period['seaSurfaceTemperatureC'],
                "seaCurrentSpeedMPS": period['seaCurrentSpeedMPS'],
                "seaCurrentDir": period['seaCurrentDir'],
                "seaCurrentDirDEG": period['seaCurrentDirDEG'],
                "significantWaveHeightM": period['significantWaveHeightM'],
                "primaryWaveDir": period['primaryWaveDir'],
                "primaryWaveDirDEG": period['primaryWaveDirDEG'],
                "primaryWavePeriod": period['primaryWavePeriod'],
                "tidesM": period['tidesM'],
                "surgeM": period['surgeM'],
                "windWaveDir": period['windWaveDir'],
                "windWaveDirDEG": period['windWaveDirDEG'],
                "windWavePeriod": period['windWavePeriod'],
                "latitude": lat,
                "longitude": long,
            }
            
            # Append the extracted data to the list
            data_list.append(extracted_data)

        # Convert the list of extracted data to a pandas DataFrame
        df = pd.DataFrame(data_list)

        # Print the DataFrame
        return df
    else:
        print("An error occurred: %s" % (json['error']['description']))
        request.close()
    