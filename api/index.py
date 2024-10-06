import datetime
from fastapi import FastAPI
import numpy as np
import random
from dotenv import load_dotenv

random.seed(0)
load_dotenv()

from model.demand.index import build_settlement_demand
from model.services.renewable_ninja import get_pv_output
from model.services.utilities import comparable_date
from model.hydro.index import get_hydro

app = FastAPI()


@app.get("/api/data")
def run(
    lat: float,
    lon: float,
    households: int,
    num_days: int,
    start_date: str = datetime.datetime.now().strftime("%Y-%m-%d"),
):
    unit_hydro = get_hydro(lon, lat, start_date, num_days)
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
    return {
        "E_load": list(demand),
        "E_PV": list(unit_pv),
        "E_Hydro": list(unit_hydro),
    }
