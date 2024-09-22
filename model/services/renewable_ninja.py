"""This script pulls data from the Renewable Ninja API.

Example usage:
    python renewable_ninja.py

Notes:
-   This script will not work without an API token.
-   The API token can be obtained from https://www.renewables.ninja/documentation/api
-   Change the parameters at the bottom of the script to suit your needs.
-   You will notice that many variables are hardcoded. Feel free to expose them as needed.
    However, at this time I do not feel that they are needed and the defaults should suffice for our use case.


"""
from datetime import timedelta, datetime
import json
import os

import http.client
import urllib.parse

def make_get_request(base_url, query_params=None, headers=None):
    # Parse the base URL
    parsed_url = urllib.parse.urlparse(base_url)

    # Construct the query string if any query parameters are provided
    if query_params:
        query_string = urllib.parse.urlencode(query_params)
        path = f"{parsed_url.path}?{query_string}"
    else:
        path = parsed_url.path

    # Create a connection (assuming HTTP; use HTTPSConnection for secure URLs)
    conn = http.client.HTTPSConnection(parsed_url.hostname)

    # Set headers if provided, otherwise set to empty dict
    headers = headers if headers else {}

    # Send the GET request
    conn.request("GET", path, headers=headers)

    # Get the response
    response = conn.getresponse()

    # Read and decode the response data
    data = response.read().decode()

    # Close the connection
    conn.close()

    return {
        "status": response.status,
        "reason": response.reason,
        "headers": response.getheaders(),
        "data": data
    }

# >> IMPORTANT: get your own token from https://www.renewables.ninja/documentation/api <<
# and add as an environment variable << ask chat gpt if you don't know how
# This script will not work without it!
API_TOKEN = os.getenv('RENEWABLES_NINJA_API_TOKEN')

BASE_URL = 'https://www.renewables.ninja/api/data'


def get_heating_demand(start_date, end_date, lat, lon):
    """Pulls daily demand data for a given location + time period.

    Args:
        start_date (str): start date in YYYY-MM-DD format
        end_date (str): end date in YYYY-MM-DD format
        lat (float): latitude
        lon (float): longitude

    Returns:
        dict: demand data
    """
    base_url = f"{BASE_URL}/demand"

    # Parameters for the API call
    params = {
        "local_time": "true",
        "lat": lat,
        "lon": lon,
        "date_from": start_date,
        "date_to": end_date,
        "dataset": "merra2",
        "heating_threshold": 14,
        "cooling_threshold": 20,
        "base_power": 0,
        "heating_power": 0.3,
        "cooling_power": 0.15,
        "smoothing": 0.5,
        "solar_gains": 0.012,
        "wind_chill": -0.2,
        "humidity_discomfort": 0.05,
        "use_diurnal_profile": "true",
        "format": "json",
        "mean": "day",
    }

    # Headers for the API call, including the authorization token
    headers = {"Authorization": f"Token {API_TOKEN}"}

    # Make the GET request to the API
    response = make_get_request(base_url, params, headers)

    # Check if the request was successful
    if response['status'] == 200:
        # Return the JSON data
        data = json.loads(response['data'])['data']
        return data
    else:
        # Handle errors
        raise Exception(f"Request failed with status code {response['status']}: {response['reason']}")

def get_pv_output(start_date, end_date, lat, lon):
    """Pulls hourly PV output for a given location + time period.

    Args:
        start_date (str): start date in YYYY-MM-DD format
        end_date (str): end date in YYYY-MM-DD format
        lat (float): latitude
        lon (float): longitude

    Returns:
        dict: unit PV output per hour, which assumes capacity of 1
    """
    base_url = f"{BASE_URL}/pv"

    # add one day to each date without pandas
    adj_start_date = (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=-1)).strftime('%Y-%m-%d')
    adj_end_date = (datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

    # Parameters for the API call
    params = {
        "local_time": "true",
        "lat": lat,
        "lon": lon,
        "date_from": adj_start_date,
        "date_to": adj_end_date,
        "dataset": "merra2",
        "capacity": 1,
        "system_loss": 0.1,
        "tracking": 0,
        "tilt": 35,
        "azim": 180,
        "format": "json",
    }

    # Headers for the API call, including the authorization token
    headers = {"Authorization": f"Token {API_TOKEN}"}

    # Make the GET request to the API
    response = make_get_request(base_url, params, headers)

    # Check if the request was successful
    if response['status'] == 200:
        data = json.loads(response['data'])['data']
        filtered = [(d['local_time'][:10], d['local_time'], d['electricity']) for d in data.values() if start_date <= d['local_time'][:10] <= end_date]
        # Return the JSON data
        return [d[2] for d in filtered]
    else:
        # Handle errors
        raise Exception(f"Request failed with status code {response['status']}: {response['reason']}")
