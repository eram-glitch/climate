from django.shortcuts import render
from django.http import HttpResponse

from django.conf import settings
import requests
from .utils.data_processor import *

def home(request):
    context = {
        'temperature': [],
        'cyclones': [],
        'earthquakes': []
    }

    # NASA Temperature Data (no auth)
    try:
        nasa_response = requests.get(
            "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.json",
            timeout=15
        )
        nasa_response.raise_for_status()
        nasa_data = nasa_response.json()
        context['temperature'] = process_nasa_temp(nasa_data)
        print(f"NASA: {len(context['temperature'])} entries | Sample: {context['temperature'][:1]}")
    except Exception as e:
        print(f"NASA Error: {str(e)}")


        # USGS Earthquake Data
        try:
            usgs_response = requests.get(
                "https://earthquake.usgs.gov/fdsnws/event/1/query",
                params={'format': 'geojson', 'minmagnitude': 4.5, 'limit': 200},
                timeout=10
            )
            usgs_response.raise_for_status()
            quake_data = usgs_response.json()
            context['earthquakes'] = process_earthquakes(quake_data)
            print(f"USGS: {len(context['earthquakes'])} quakes")
        except Exception as e:
            print(f"USGS Error: {str(e)}")

    # GDACS Real-time Cyclone Alerts
    try:
        gdacs_response = requests.get(
            "https://www.gdacs.org/gdacsapi/api/events/geteventlist/METEOROLOGICAL/1",
            timeout=10
        )
        gdacs_response.raise_for_status()
        alert_data = gdacs_response.json()

        context['cyclones'] = process_gdacs_cyclones(alert_data)
        print(f"GDACS: {len(context['cyclones'])} cyclone alerts")
    except Exception as e:
        print(f"GDACS Cyclone Error: {str(e)}")


    return render(request, 'climate_app/home.html', context)