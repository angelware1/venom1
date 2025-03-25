import subprocess
import time

class SimpleNetworkDiscovery:
    def __init__(self):
        self.devices = []
        self.logs = []

    def discover(self):
        print(f"Scanning network at {time.ctime()}")
        self.logs.append(f"Scanning network at {time.ctime()}")
        try:
            # Run arp -a to get devices
            result = subprocess.check_output(["arp", "-a"], text=True)
            self.logs.append("ARP scan completed")
            lines = result.splitlines()
            for line in lines:
                if "(" in line and ")" in line:
                    ip = line.split("(")[1].split(")")[0]
                    mac_start = line.find("at ")
                    if mac_start != -1:
                        mac = line[mac_start + 3:].split(" ")[0]
                        self.devices.append({"ip": ip, "mac": mac})
                        self.logs.append(f"Found: {ip} ({mac})")
            if not self.devices:
                self.logs.append("No devices found in ARP cache")
        except subprocess.CalledProcessError as e:
            self.logs.append(f"Error running arp -a: {e}. Run with sudo for better results.")
        except Exception as e:
            self.logs.append(f"Unexpected error: {e}")

    def get_results(self):
        return self.devices, self.logs

if __name__ == "__main__":
    discovery = SimpleNetworkDiscovery()
    discovery.discover()
    devices, logs = discovery.get_results()
    print("Devices:", devices)
    print("Logs:", logs)
