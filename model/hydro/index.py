import datetime
import math
from datetime import timedelta
from model.services.utilities import comparable_date
from model.hydro.river_flow import river_flow

river_stations = [
    {
        "Station_Number": "2260100",
        "Station_Name": "HKAMTI",
        "Latitude": 26.0,
        "Longitude": 95.7,
    },
    {
        "Station_Number": "2260110",
        "Station_Name": "MAWLAIK",
        "Latitude": 23.63,
        "Longitude": 94.42,
    },
    {
        "Station_Number": "2260120",
        "Station_Name": "MONYWA",
        "Latitude": 22.1,
        "Longitude": 95.13,
    },
    {
        "Station_Number": "2260400",
        "Station_Name": "KATHA",
        "Latitude": 24.17,
        "Longitude": 96.33,
    },
    {
        "Station_Number": "2260500",
        "Station_Name": "SAGAING",
        "Latitude": 21.98,
        "Longitude": 96.1,
    },
    {
        "Station_Number": "2260600",
        "Station_Name": "MAGWAY",
        "Latitude": 20.13,
        "Longitude": 94.92,
    },
    {
        "Station_Number": "2260700",
        "Station_Name": "PYAY",
        "Latitude": 18.8,
        "Longitude": 95.22,
    },
]

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) * math.sin(d_lat / 2) +
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
        math.sin(d_lon / 2) * math.sin(d_lon / 2)
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# Function to get Z-Scores for the closest station
def get_hydro(longitude, latitude, start_date, number_of_days):
    # Find the closest station
    closest_station = river_stations[0]
    min_distance = calculate_distance(
        latitude, longitude, closest_station["Latitude"], closest_station["Longitude"]
    )

    for station in river_stations[1:]:
        distance = calculate_distance(
            latitude, longitude, station["Latitude"], station["Longitude"]
        )
        if distance < min_distance:
            closest_station = station
            min_distance = distance

    # Get Z-Scores for the closest station
    station_number = closest_station["Station_Number"]
    station_flow_data = [
        data for data in river_flow if data["Station_Number"] == station_number
    ]

    # Generate the Z-Scores for each day
    results = []
    current_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")

    for _ in range(number_of_days):
        date = current_date.strftime("%Y-%m-%d")
        comparable = comparable_date(date)
        flow_data = next(
            (data for data in station_flow_data if data["date"] == comparable), None
        )
        results.append(flow_data["norm"])

        # Move to the next day
        current_date += timedelta(days=1)

    return [rr for r in results for rr in [r] * 24]
