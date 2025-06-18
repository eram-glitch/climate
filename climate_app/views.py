from django.shortcuts import render
from django.core.cache import cache
from django.conf import settings
import requests
from django.http import JsonResponse

from .utils.data_processor import process_earthquakes, process_fires_from_csv
from .utils.gdacs_handler import fetch_gdacs_events
from gdacs.api import GDACSAPIReader
from datetime import date



def home(request):
    return render(request, "home.html")




def disaster_data_api(request):
    context = {
        'earthquakes': [],
        'cyclones': [],
        'floods': [],
        'droughts': [],
        'fires': [],
    }

    try:
        usgs_response = requests.get(
            "https://earthquake.usgs.gov/fdsnws/event/1/query",
            params={
                'format': 'geojson',
                'minmagnitude': 4.0,
                'starttime': f'{date.today().year}-01-01',
                'endtime': f'{date.today()}',
                'orderby': 'time',
            },
            timeout=10
        )
        usgs_response.raise_for_status()
        quake_data = usgs_response.json()
        context['earthquakes'] = process_earthquakes(quake_data)
    except Exception as e:
        print(f"USGS Error: {e}")

    try:
        all_events = fetch_gdacs_events(limit=25)
        context["cyclones"] = [e for e in all_events if e["type"] == "TC"]
        context["floods"] = [e for e in all_events if e["type"] == "FL"]
        context["droughts"] = [e for e in all_events if e["type"] == "DR"]
    except Exception as e:
        print(f"GDACS Error: {e}")

    try:
        fire_csv_path = "climate_app/static/data/firms_7d.csv"
        context['fires'] = process_fires_from_csv(fire_csv_path)
    except Exception as e:
        print(f"FIRMS Error: {e}")

    return JsonResponse(context)



def climate_change_view(request):
    return render(request, "climate_change.html")
