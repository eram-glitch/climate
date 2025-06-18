from datetime import datetime
import csv


def process_earthquakes(usgs_data):
    quakes = []
    for feature in usgs_data.get('features', []):
        try:
            coords = feature['geometry']['coordinates']
            props = feature['properties']
            quakes.append({
                'lat': coords[1],
                'lng': coords[0],
                'mag': props['mag'],
                'place': props.get('place', 'Location unavailable'),
                'time': props['time']
            })
        except Exception as e:
            print(f"Quake processing error: {str(e)}")
    return quakes


def process_fires_from_csv(file_path):
    fires = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                lat = float(row['latitude'])
                lon = float(row['longitude'])
                confidence = row.get('confidence', '')
                date = row.get('acq_date', '')
                time = row.get('acq_time', '')
                fires.append({
                    'lat': lat,
                    'lng': lon,
                    'confidence': confidence,
                    'datetime': f"{date} {time}"
                })
            except Exception as e:
                print(f"Fire parse error: {e}")
    return fires
