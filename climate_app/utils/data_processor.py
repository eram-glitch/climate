def process_nasa_temp(nasa_data):
    processed = []
    for entry in nasa_data.get('data', []):
        try:
            # Verify data structure
            if not all(key in entry for key in ['Year', 'J-D']):
                continue
                
            year = int(entry['Year'])
            if 1993 <= year <= 2023:
                anomaly = float(entry['J-D'])
                
                # New coordinate calculation (5x6 grid)
                grid_cols = 6
                row = (year - 1993) // grid_cols
                col = (year - 1993) % grid_cols
                
                lat = -75 + (row * 30)  # 30° between rows
                lng = -165 + (col * 60)  # 60° between columns
                
                processed.append({
                    'year': year,
                    'anomaly': anomaly,
                    'lat': lat,
                    'lng': lng
                })
        except Exception as e:
            print(f"Temp Error: {str(e)} | Entry: {entry}")
    return processed

# climate_app/utils/data_processor.py
def process_cyclones(ibtracs_data):
    processed = []
    try:
        # Handle different API response formats
        storms = ibtracs_data.get('data', {}).get('storms', []) if 'data' in ibtracs_data else ibtracs_data.get('storms', [])
        
        for storm in storms:
            valid_points = []
            for point in storm.get('points', []):
                try:
                    lat = float(point['lat'])
                    lon = float(point['lon'])
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        valid_points.append([lat, lon])
                except (KeyError, ValueError):
                    continue
            
            if len(valid_points) > 1:  # Require at least 2 points for a path
                processed.append({
                    'name': storm.get('name', 'Unnamed Storm'),
                    'year': storm.get('season', 'Unknown'),
                    'path': valid_points
                })
    except Exception as e:
        print(f"Cyclone processing error: {str(e)}")
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