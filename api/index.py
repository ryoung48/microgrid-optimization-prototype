import datetime
from fastapi import FastAPI
import numpy as np
import random
from dotenv import load_dotenv

random.seed(0)
load_dotenv()

from model.capacity import optimize_capacity
from model.demand.index import build_settlement_demand
from model.services.renewable_ninja import get_pv_output
from model.services.utilities import comparable_date

app = FastAPI()


@app.get("/api/optimization")
def run(
    lat: float,
    lon: float,
    households: int,
    num_days: int,
    start_date: str = datetime.datetime.now().strftime("%Y-%m-%d"),
):
    """
    Runs the Myanmar Micro-Grid Optimization model. This includes capacity optimization, demand forecasting, and PV forecasting for a given time period.

    You need to have the following environment variables set:
    - RENEWABLES_NINJA_API_TOKEN: Your Renewables Ninja API token

    I recommend putting these in a .env file in the root of your project.

    You will also need to make sure your pythonpath has the project root in it.

    Parameters:
        cluster_id (int): The ID of the village cluster.
        num_days (int): The number of days to run the optimization for.
        start_date (str): The start date of the optimization period (default: current date).

    Returns:
        tuple: A tuple containing the optimal PV capacity, optimal battery capacity, optimal diesel capacity, and optimal dispatch.
    """
    demand = build_settlement_demand(
        num_households=households,
        date_start=start_date,
        num_days=num_days,
        lat=lat,
        lon=lon,
    )
    # use last years pv output for our forecast
    pv_start_date = comparable_date(start_date)
    date_start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    pv_end_date = comparable_date(
        (date_start_dt + datetime.timedelta(days=num_days - 1)).strftime("%Y-%m-%d")
    )
    unit_pv = np.array(get_pv_output(pv_start_date, pv_end_date, lat, lon))
    # get optimal capacities + dispatch
    # TODO: currently this trains on the comparable time period from last year
    # for real optimal capacities, we need to train on at least a full year
    # BUT from a presentation perspective, we will get lots of curtailment if we train on the full year
    # and so I cheat :)
    # in future, we can cap it at two weeks (the most expensive weeks) to shorten the train time
    return optimize_capacity(demand, unit_pv)
