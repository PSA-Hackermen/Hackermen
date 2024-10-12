from constants import MARITIME_POINTS
import pandas as pd
import urllib
import json as j
import dotenv
import matplotlib.pyplot as plt
from api import langchain_api

llm_client = langchain_api.OpenAIClient()

def findRoute(source_dock, dest_dock, sailing_speed, travel_duration):
    # sailing_speed is a tuple of (min_speed, max_speed)
    # travel_duration is an integer representing the max number of hours to travel

    merged_df = pd.DataFrame()
    figure = None  # Initialize figure to handle cases where it's not defined
    for coordinates in MARITIME_POINTS.values():
        lat, long = coordinates
        df, figure = callAPI(lat, long)  # Assuming callAPI returns (DataFrame, Figure)
        
        # Only concatenate if df is not empty
        if not df.empty:
            if merged_df.empty:
                merged_df = df
            else:
                merged_df = pd.concat([merged_df, df], ignore_index=True)

    # Convert DataFrame to a list of dictionaries
    df_dict = merged_df.to_dict(orient='records')
    for data in df_dict:
        if 'dateTimeISO' in data:
            del data['dateTimeISO']
    # Create the object for the API call
    obj = {
        "source_dock": source_dock,
        "dest_dock": dest_dock,
        "sailing_speed": sailing_speed,
        "travel_duration": travel_duration,
        "api_data": j.dumps(df_dict)
    }

    route_list = llm_client.generate(j.dumps(obj))
    print(route_list)

    return merged_df, figure, route_list

def callAPI(mt_lat, mt_long):
    values = dotenv.dotenv_values(".env")
    request = urllib.request.urlopen(f'https://data.api.xweather.com/maritime/{mt_lat},{mt_long}?filter=1hr&client_id={values["CLIENT_ID"]}&client_secret={values["CLIENT_SECRET"]}&plimit=1')
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
                "dateTimeISO": period.get('dateTimeISO', None),
                "seaSurfaceTemperatureC": period.get('seaSurfaceTemperatureC', None),
                "seaCurrentSpeedMPS": period.get('seaCurrentSpeedMPS', None),
                "seaCurrentDir": period.get('seaCurrentDir', None),
                "seaCurrentDirDEG": period.get('seaCurrentDirDEG', None),
                "significantWaveHeightM": period.get('significantWaveHeightM', None),
                "primaryWaveDir": period.get('primaryWaveDir', None),
                "primaryWaveDirDEG": period.get('primaryWaveDirDEG', None),
                "primaryWavePeriod": period.get('primaryWavePeriod', None),
                "tidesM": period.get('tidesM', None),
                "surgeM": period.get('surgeM', None),
                "windWaveDir": period.get('windWaveDir', None),
                "windWaveDirDEG": period.get('windWaveDirDEG', None),
                "windWavePeriod": period.get('windWavePeriod', None),
                "latitude": lat,
                "longitude": long,
            }
            
            # Append the extracted data to the list
            data_list.append(extracted_data)

        # Convert the list of extracted data to a pandas DataFrame
        df = pd.DataFrame(data_list)

        # prevent timezone localisation
        df["dateTimeISO"] = pd.to_datetime(df["dateTimeISO"]).dt.tz_localize(None)
        df["seaCurrentDir"] = df["seaCurrentDir"].astype("category")
        df["primaryWaveDir"] = df["primaryWaveDir"].astype("category")
        df["windWaveDir"] = df["windWaveDir"].astype("category")

        fig, axis = plt.subplots(figsize=(12, 12))
        axis.set_xlabel('Time')
        axis.set_ylabel('Sea Surface Temp (°C)', color='tab:red')
        axis.plot(df['dateTimeISO'], df['seaSurfaceTemperatureC'], color='tab:red', label='Sea Surface Temp (°C)')
        axis.tick_params(axis='y', labelcolor='tab:red')

        # Create a secondary y-axis for sea current speed
        ax2 = axis.twinx()
        ax2.set_ylabel('Sea Current Speed (m/s)', color='tab:blue')
        ax2.plot(df['dateTimeISO'], df['seaCurrentSpeedMPS'], color='tab:blue', label='Sea Current Speed (m/s)')
        ax2.tick_params(axis='y', labelcolor='tab:blue')

        # Create another y-axis for significant wave height
        ax3 = axis.twinx()
        ax3.spines['right'].set_position(('outward', 60))  # Move the third y-axis out to avoid overlap
        ax3.set_ylabel('Significant Wave Height (m)', color='tab:green')
        ax3.plot(df['dateTimeISO'], df['significantWaveHeightM'], color='tab:green', label='Wave Height (m)')
        ax3.tick_params(axis='y', labelcolor='tab:green')

        # Create a fourth y-axis for tides
        ax4 = axis.twinx()
        ax4.spines['right'].set_position(('outward', 120))  # Move the fourth y-axis further out
        ax4.set_ylabel('Tides (m)', color='tab:orange')
        ax4.plot(df['dateTimeISO'], df['tidesM'], color='tab:orange', label='Tides (m)')
        ax4.tick_params(axis='y', labelcolor='tab:orange')

        # Create a fifth y-axis for surge
        ax5 = axis.twinx()
        ax5.spines['right'].set_position(('outward', 180))  # Move the fifth y-axis further out
        ax5.set_ylabel('Surge (m)', color='tab:purple')
        ax5.plot(df['dateTimeISO'], df['surgeM'], color='tab:purple', label='Surge (m)')
        ax5.tick_params(axis='y', labelcolor='tab:purple')

        # Title and layout adjustments
        plt.title(f"Environmental Data Plot at Location (Lat: {lat}, Long: {long})")
        fig.tight_layout()

        # Print the DataFrame
        return df, fig
    else:
        print("An error occurred: %s" % (json['error']['description']))
        request.close()
    