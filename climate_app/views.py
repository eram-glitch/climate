from django.shortcuts import render
from django.http import HttpResponse


from django.shortcuts import render
from django.conf import settings
import requests
from .utils.data_processor import *

def home(request):
    context = {
        'temperature': [],
        'cyclones': [],
        'earthquakes': []
    }

    # NASA Temperature Data
    try:
        nasa_response = requests.get(
            "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.json",
            auth=settings.NASA_CREDS,
            timeout=15
        )
        nasa_response.raise_for_status()
        nasa_data = nasa_response.json()
        context['temperature'] = process_nasa_temp(nasa_data)
        print(f"NASA: {len(context['temperature'])} temp entries | Sample: {context['temperature'][:1]}")# Add debug logging
        print(f"NASA Raw Data: {nasa_data.get('data', [])[:2]}")

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

    # IBTrACS Cyclone Data
    try:
        # IBTrACS request with proper authentication
        ibtracs_response = requests.get(
            "https://www.ncei.noaa.gov/ibtracs/php/IDBsearch.php",
            params={
                'format': 'json',
                'basin': 'all',
                'start_year': '1993',
                'end_year': '2023',
                'units': 'degrees'
            },
            headers={'Authorization': f'Bearer {settings.IBTRACS_API_KEY}'},
            timeout=20
        )
        
        print(f"IBTrACS Status: {ibtracs_response.status_code}")
        print(f"IBTrACS Response Sample: {ibtracs_response.text[:500]}")  # Log response start
        
        if ibtracs_response.status_code == 200:
            cyclone_data = ibtracs_response.json()
            # Handle different response formats
            storms = cyclone_data.get('data', {}).get('storms', []) if 'data' in cyclone_data else cyclone_data.get('storms', [])
            context['cyclones'] = process_cyclones({'storms': storms})
            print(f"First cyclone path: {storms[0]['points'][0] if storms else 'None'}")
        else:
            print(f"IBTrACS Error: {ibtracs_response.text}")
    except Exception as e:
        print(f"IBTrACS Error: {str(e)}")

    return render(request, 'climate_app/home.html', context)