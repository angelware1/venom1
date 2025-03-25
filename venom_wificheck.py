import subprocess
import time

class VenomWifiCheck:
    def __init__(self, data_queue):
        self.data_queue = data_queue
        print("Venom WiFi Check initialized")

    async def run_once(self):
        """Scan for nearby Wi-Fi networks and push to data_queue."""
        wifi_data = self.get_wifi_networks()
        self.data_queue.put({
            "external": {
                "wifi_networks": wifi_data
            }
        })
        print(f"WiFi networks queued: {wifi_data}")

    def get_wifi_networks(self):
        """Fetch nearby Wi-Fi networks using nmcli."""
        try:
            result = subprocess.check_output(
                ["nmcli", "-f", "SSID,SIGNAL", "dev", "wifi"],
                text=True,
                timeout=10
            )
            networks = [line for line in result.splitlines() if "SSID" not in line and line.strip()]  # Skip header, empty lines
            if networks:
                return "\n".join(networks)  # Format: "SSID  SIGNAL"
            return "No Wi-Fi networks detected"
        except subprocess.CalledProcessError as e:
            print(f"WiFi scan error: {e}")
            return "WiFi scan failed - check network manager"
        except subprocess.TimeoutExpired:
            print("WiFi scan timed out")
            return "WiFi scan timed out"
