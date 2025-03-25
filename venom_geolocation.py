import requests
import time
from datetime import datetime

class VenomGeolocation:
    def __init__(self, data_queue):
        self.data_queue = data_queue
        print("Venom Geolocation initialized")

    async def run_once(self):
        """Fetch geolocation and push to data_queue."""
        location = self.get_geolocation()
        if location:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            geo_data = f"{timestamp} - IP: {location['ip']}, {location['city']}, {location['region']}, {location['country']} ({location['latitude']}, {location['longitude']})"
            self.data_queue.put({
                "external": {
                    "geolocation": geo_data
                }
            })
            print(f"Geolocation queued: {geo_data}")
        else:
            self.data_queue.put({
                "external": {
                    "geolocation": "Failed to fetch geolocation"
                }
            })
            print("Geolocation fetch failed")

    def get_geolocation(self):
        """Fetch geolocation data from ip-api.com."""
        try:
            response = requests.get('http://ip-api.com/json/', timeout=5)
            data = response.json()
            if data['status'] == 'success':
                return {
                    "ip": data['query'],
                    "city": data['city'],
                    "region": data['regionName'],
                    "country": data['country'],
                    "latitude": data['lat'],
                    "longitude": data['lon']
                }
            else:
                print(f"API failed: {data.get('message', 'Unknown error')}")
                return None
        except requests.RequestException as e:
            print(f"Error fetching geolocation: {e}")
            return None
