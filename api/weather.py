from constants import MARITIME_POINTS
import pandas as pd
import urllib
import json as j
import dotenv
import matplotlib.pyplot as plt
from api import langchain_api

llm_client = langchain_api.OpenAIClient()

values = dotenv.dotenv_values(".env")

def findRoute(source_dock, dest_dock, sailing_speed, travel_duration):
    # sailing_speed is a tuple of (min_speed, max_speed)
    # travel_duration is an integer representing the max number of hours to travel
    
    merged_maritime, merged_weather = pd.DataFrame(), pd.DataFrame()
    loaded_maritime, loaded_weather = False, False

    for lat, long in MARITIME_POINTS.values():
        if loaded_maritime and loaded_weather:
            break

        if merged_maritime.empty:
            try:
                merged_maritime = get_maritime_api(lat, long)
            except:
                loaded_maritime = True
                merged_maritime = pd.read_csv("maritime.csv", index_col=0, header="infer").reset_index(drop=True)
        else:
            merged_maritime = pd.concat([merged_maritime, get_maritime_api(lat, long)], ignore_index=True)
        
        if merged_weather.empty:
            try:
                merged_weather = get_weather_api(lat, long)
            except:
                loaded_weather = True
                merged_weather = pd.read_csv("weather.csv", index_col=0, header="infer").reset_index(drop=True)
        else:
            merged_weather = pd.concat([merged_weather, get_weather_api(lat, long)], ignore_index=True)
    
    df_maritime, df_weather = merged_maritime.to_dict(orient="records"), merged_weather.to_dict(orient="records")
    
    for data in df_maritime:
        if "dateTimeISO" in data:
            del data["dateTimeISO"]
    
    for data in df_weather:
        if "dateTimeISO" in data:
            del data["dateTimeISO"]

    obj = {
        "source_dock": source_dock,
        "dest_dock": dest_dock,
        "sailing_speed": sailing_speed,
        "travel_duration": travel_duration,
        "api_data": [df_maritime, df_weather]
    }

    route_list = llm_client.generate(j.dumps(obj))

    return merged_maritime, merged_weather, get_maritime_figure(merged_maritime), get_weather_figure(merged_weather), route_list

def get_maritime_figure(merged):
    # prevent timezone localisation
    merged["dateTimeISO"] = pd.to_datetime(merged["dateTimeISO"]).dt.tz_localize(None)
    merged["seaCurrentDir"] = merged["seaCurrentDir"].astype("category")
    merged["primaryWaveDir"] = merged["primaryWaveDir"].astype("category")
    merged["windWaveDir"] = merged["windWaveDir"].astype("category")

    fig, axis = plt.subplots(3, 2, figsize=(12, 12), subplot_kw=dict(projection='3d'))
    axis = axis.flatten()
    depths = [1 for i in range(len(merged))]
    height_depths = [i for i in range(len(merged))]
    
    axis[0].bar3d(merged['latitude'], merged['longitude'], merged["seaSurfaceTemperatureC"], dx=depths, dy=depths, dz=height_depths, color='tab:red', label='Sea Surface Temp (°C)', shade=True)
    axis[0].set_xlabel('Latitude')
    axis[0].set_ylabel('Longitude')
    axis[0].set_zlabel('Sea Surface Temp (°C)', color='tab:red')

    # Create a secondary y-axis for sea current speed
    axis[1].bar3d(merged['latitude'], merged['longitude'], merged["seaCurrentSpeedMPS"], dx=depths, dy=depths, dz=height_depths, color='tab:blue', label='Sea Current Speed (m/s)', shade=True)
    axis[1].set_xlabel('Latitude')
    axis[0].set_ylabel('Longitude')
    axis[1].set_zlabel('Sea Current Speed (m/s)', color='tab:blue')

    # Create another y-axis for significant wave height
    axis[2].bar3d(merged['latitude'], merged['longitude'], merged["significantWaveHeightM"], dx=depths, dy=depths, dz=height_depths, color='tab:green', label='Wave Height (m)', shade=True)
    axis[2].set_xlabel('Latitude')
    axis[0].set_ylabel('Longitude')
    axis[2].set_zlabel('Wave Height (m)', color='tab:green')

    # Create a fourth y-axis for tides
    axis[3].bar3d(merged['latitude'], merged['longitude'], merged["tidesM"], dx=depths, dy=depths, dz=height_depths, color='tab:orange', label='Tides (m)', shade=True)
    axis[3].set_xlabel('Latitude')
    axis[0].set_ylabel('Longitude')
    axis[3].set_zlabel('Tides (m)', color='tab:orange')

    # Create a fifth y-axis for surge
    axis[4].bar3d(merged['latitude'], merged['longitude'], merged["surgeM"], dx=depths, dy=depths, dz=height_depths, color='tab:purple', label='Surge (m)', shade=True)
    axis[4].set_xlabel('Latitude')
    axis[0].set_ylabel('Longitude')
    axis[4].set_zlabel('Surge (m)', color='tab:purple')

    # Title and layout adjustments
    fig.suptitle(f"Maritime Data Plot")
    fig.tight_layout()
    
    return fig


def get_weather_figure(merged):
    print(merged.columns)
    # Set up the subplots (2 columns x 3 rows for 6 variables)
    fig, axes = plt.subplots(3, 2, figsize=(10, 10), sharex=True, sharey=True)

    # Flatten the axes for easy indexing
    axes = axes.flatten()

    # Plot each variable based on latitude and longitude
    axes[0].scatter(merged['longitude'], merged['latitude'], c=merged['tempC'], label='Temp (°C)', cmap='coolwarm', marker='o')
    axes[0].set_title('Temperature (°C)')
    axes[0].set_ylabel('Latitude')
    axes[0].set_xlabel('Longitude')

    axes[1].scatter(merged['longitude'], merged['latitude'], c=merged['feelslikeC'], label='Feels Like (°C)', cmap='coolwarm', marker='o')
    axes[1].set_title('Feels Like (°C)')
    axes[1].set_xlabel('Longitude')

    axes[2].scatter(merged['longitude'], merged['latitude'], c=merged['dewpointC'], label='Dewpoint (°C)', cmap='Blues', marker='o')
    axes[2].set_title('Dewpoint (°C)')
    axes[2].set_ylabel('Latitude')
    axes[2].set_xlabel('Longitude')

    axes[3].scatter(merged['longitude'], merged['latitude'], c=merged['humidity'], label='Humidity (%)', cmap='Purples', marker='o')
    axes[3].set_title('Humidity (%)')
    axes[3].set_xlabel('Longitude')

    axes[4].scatter(merged['longitude'], merged['latitude'], c=merged['windSpeedKPH'], label='Wind Speed (KPH)', cmap='Reds', marker='o')
    axes[4].set_title('Wind Speed (KPH)')
    axes[4].set_ylabel('Latitude')
    axes[4].set_xlabel('Longitude')

    axes[5].scatter(merged['longitude'], merged['latitude'], c=merged['pressureMB'], label='Pressure (MB)', cmap='Greens', marker='o')
    axes[5].set_title('Pressure (MB)')
    axes[5].set_xlabel('Longitude')

    # Add a title
    fig.suptitle('Weather Data Plot')
    fig.tight_layout()
    
    return fig


def get_maritime_api(mt_lat, mt_long):
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
            try:
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
            except:
                continue
        
        df = pd.DataFrame(data_list)
        df["dateTimeISO"] = pd.to_datetime(df["dateTimeISO"], utc=True)
        
        return df
    else:
        print("An error occurred: %s" % (json['error']['description']))
        request.close()
    
def get_weather_api(lat, lon):
    request = urllib.request.urlopen(f'https://data.api.xweather.com/conditions/{lat},{lon}?filter=1hr&client_id={values["CLIENT_ID"]}&client_secret={values["CLIENT_SECRET"]}&plimit=1')
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
            try:
                extracted_data = {
                    "dateTimeISO": period['dateTimeISO'],
                    "tempC": period["tempC"],
                    "feelslikeC": period["feelslikeC"],
                    "dewpointC": period["dewpointC"],
                    "humidity": period["humidity"],
                    "pressureMB": period["pressureMB"],
                    "windDir": period["windDir"],
                    "windDirDEG": period["windDirDEG"],
                    "windSpeedKPH": period["windSpeedKPH"],
                    "windGustKPH": period["windGustKPH"],
                    "precipMM": period["precipMM"],
                    "precipRateMM": period["precipRateMM"],
                    "snowCM": period["snowCM"],
                    "snowRateCM": period["snowRateCM"],
                    "snowDepthCM": period["snowDepthCM"],
                    "pop": period["pop"],
                    "visibilityKM": period["visibilityKM"],
                    "sky": period["sky"],
                    "cloudsCoded": period["cloudsCoded"],
                    "weather": period["weather"],
                    "weatherCoded": period["weatherCoded"],
                    "weatherPrimary": period["weatherPrimary"],
                    "weatherPrimaryCoded": period["weatherPrimaryCoded"],
                    "icon": period["icon"],
                    "solradWM2": period["solradWM2"],
                    "uvi": period["uvi"],
                    "isDay": period["isDay"],
                    "spressureMB": period["spressureMB"],
                    "altimeterMB": period["altimeterMB"],
                    "solrad": {
                        "azimuthDEG": period["solrad"]["azimuthDEG"],
                        "zenithDEG": period["solrad"]["zenithDEG"],
                        "ghiWM2": period["solrad"]["ghiWM2"],
                        "dniWM2": period["solrad"]["dniWM2"]
                    },
                    "latitude": lat,
                    "longitude": long,
                }
                
                # Append the extracted data to the list
                data_list.append(extracted_data)
            except:
                continue

        # Convert the list of extracted data to a pandas DataFrame
        df = pd.DataFrame(data_list)
        df["dateTimeISO"] = pd.to_datetime(df["dateTimeISO"], utc=True)

        return df
    else:
        print("An error occurred: %s" % (json['error']['description']))
        request.close()
