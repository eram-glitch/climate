from datetime import datetime

def process_nasa_temp(nasa_data):
    current_month = datetime.utcnow().strftime('%b')  # e.g., "Apr"
    processed = []
    
    # Create a more realistic global grid
    for lat in range(-90, 91, 15):  # Every 15 degrees of latitude
        for lng in range(-180, 181, 30):  # Every 30 degrees of longitude
            # Find the average temperature anomaly for this month across years
            total_anomaly = 0
            count = 0
            for entry in nasa_data.get('data', []):
                try:
                    year = int(entry['Year'])
                    if 1993 <= year <= 2023:  # Last 30 years
                        anomaly = float(entry.get(current_month, 0) or 0)
                        total_anomaly += anomaly
                        count += 1
                except Exception as e:
                    print(f"Temp Error: {str(e)} | Entry: {entry}")
            
            if count > 0:
                avg_anomaly = total_anomaly / count
                processed.append({
                    'lat': lat,
                    'lng': lng,
                    'anomaly': avg_anomaly
                })
    
    return processed

def process_gdacs_cyclones(alert_data):
    processed = []
    for alert in alert_data.get('events', []):
        try:
            lat = float(alert.get('lat'))
            lon = float(alert.get('lon'))
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                processed.append({
                    'name': alert.get('eventname', 'Unnamed Cyclone'),
                    'year': alert.get('fromdate', '')[:4],
                    'path': [[lat, lon]]
                })
        except Exception as e:
            print(f"GDACS cyclone parse error: {str(e)}")
    return processed


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