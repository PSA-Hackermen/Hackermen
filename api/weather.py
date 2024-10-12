from constants import MARITIME_POINTS
import pandas as pd
import urllib
import json as j
import dotenv
import matplotlib.pyplot as plt

values = dotenv.dotenv_values(".env")

def findRoute(source_dock, dest_dock, sailing_speed, travel_duration):
    # sailing_speed is a tuple of (min_speed, max_speed)
    # travel_duration is an integer representing the max number of hours to travel
    
    merged_maritime, merged_weather = pd.DataFrame(), pd.DataFrame()

    for lat, long in MARITIME_POINTS.values():
        if merged_maritime.empty:
            merged_maritime = get_maritime_api(lat, long)
        else:
            merged_maritime = pd.concat([merged_maritime, get_maritime_api(lat, long)], ignore_index=True)
        
        if merged_weather.empty:
            merged_weather = get_weather_api(lat, long)
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

    json_object = j.dumps(obj)
    print(json_object)

    return merged_maritime, merged_weather, get_maritime_figure(merged_maritime), get_weather_figure(merged_weather)

def get_maritime_figure(merged):
    # prevent timezone localisation
    merged["dateTimeISO"] = pd.to_datetime(merged["dateTimeISO"]).dt.tz_localize(None)
    merged["seaCurrentDir"] = merged["seaCurrentDir"].astype("category")
    merged["primaryWaveDir"] = merged["primaryWaveDir"].astype("category")
    merged["windWaveDir"] = merged["windWaveDir"].astype("category")

    fig, axis = plt.subplots(figsize=(12, 12))
    axis.set_xlabel('Time')
    axis.set_ylabel('Sea Surface Temp (°C)', color='tab:red')
    axis.plot(merged['dateTimeISO'], merged['seaSurfaceTemperatureC'], color='tab:red', label='Sea Surface Temp (°C)')
    axis.tick_params(axis='y', labelcolor='tab:red')

    # Create a secondary y-axis for sea current speed
    ax2 = axis.twinx()
    ax2.set_ylabel('Sea Current Speed (m/s)', color='tab:blue')
    ax2.plot(merged['dateTimeISO'], merged['seaCurrentSpeedMPS'], color='tab:blue', label='Sea Current Speed (m/s)')
    ax2.tick_params(axis='y', labelcolor='tab:blue')

    # Create another y-axis for significant wave height
    ax3 = axis.twinx()
    ax3.spines['right'].set_position(('outward', 60))  # Move the third y-axis out to avoid overlap
    ax3.set_ylabel('Significant Wave Height (m)', color='tab:green')
    ax3.plot(merged['dateTimeISO'], merged['significantWaveHeightM'], color='tab:green', label='Wave Height (m)')
    ax3.tick_params(axis='y', labelcolor='tab:green')

    # Create a fourth y-axis for tides
    ax4 = axis.twinx()
    ax4.spines['right'].set_position(('outward', 120))  # Move the fourth y-axis further out
    ax4.set_ylabel('Tides (m)', color='tab:orange')
    ax4.plot(merged['dateTimeISO'], merged['tidesM'], color='tab:orange', label='Tides (m)')
    ax4.tick_params(axis='y', labelcolor='tab:orange')

    # Create a fifth y-axis for surge
    ax5 = axis.twinx()
    ax5.spines['right'].set_position(('outward', 180))  # Move the fifth y-axis further out
    ax5.set_ylabel('Surge (m)', color='tab:purple')
    ax5.plot(merged['dateTimeISO'], merged['surgeM'], color='tab:purple', label='Surge (m)')
    ax5.tick_params(axis='y', labelcolor='tab:purple')

    # Title and layout adjustments
    plt.title(f"Environmental Data Plot")
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

    # Add a color bar to the last plot to represent the data range
    fig.colorbar(axes[5].collections[0], ax=axes, location='right', pad=0.01)

    # Add a title
    fig.suptitle('Weather Variables by Latitude and Longitude')


def get_maritime_api(mt_lat, mt_long):
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
    request = urllib.request.urlopen(f'https://data.api.xweather.com/conditions/{lat},{lon}?filter=1hr&client_id={values["CLIENT_ID"]}&client_secret={values["CLIENT_SECRET"]}')
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
