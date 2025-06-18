from gdacs.api import GDACSAPIReader, GDACSAPIError

def fetch_gdacs_events(limit=20):
    client = GDACSAPIReader()
    events = []

    try:
        for event_type in ["TC", "FL", "DR"]:
            type_events = client.latest_events(event_type=event_type, limit=limit)

            for entry in type_events:
                if not isinstance(entry, tuple):
                    continue  # ignore non-tuple entries

                key, value = entry

                # We are only interested in 'features'
                if key != "features":
                    continue

                for feature in value:
                    props = feature.get("properties", {})
                    geom = feature.get("geometry", {})

                    coords = geom.get("coordinates")
                    if not coords or len(coords) != 2:
                        print(f"⚠️ Skipping feature with invalid coords: {props.get('eventname', 'Unknown')}")
                        continue

                    lat, lon = coords[1], coords[0]

                    events.append({
                        "name": props.get("eventname", "Unknown"),
                        "type": props.get("eventtype", event_type),
                        "alert_level": props.get("alertlevel", "N/A"),
                        "fromdate": props.get("fromdate", ""),
                        "todate": props.get("todate", ""),
                        "lat": lat,
                        "lon": lon,
                        "severity": props.get("severitydata", {}).get("severity"),
                        "gdacs_id": props.get("eventid", "N/A"),
                        "episode_id": props.get("episodeid", "N/A")
                    })

    except GDACSAPIError as e:
        print(f"❌ GDACS API Error: {str(e)}")

    return events
