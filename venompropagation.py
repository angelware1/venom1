import subprocess
import time
from queue import Queue

class VenomPropagation:
    def __init__(self, data_queue):
        self.data_queue = data_queue
        self.targets = []
        self.latest_versions = {"python3": "3.12.0", "bash": "5.2.21", "kernel": "6.11.2-amd64"}
        print("Venom Propagation initialized")

    async def run_once(self):
        current_data = self.get_latest_data()
        if not current_data:
            print("No data available for propagation analysis")
            return
        self.targets = self.find_potential_targets(current_data)
        target_count = len(self.targets)
        target_details = f"Last Scan: {time.ctime()}\n" + "\n".join([f"IP: {t['ip']}, Score: {t['score']}, Outdated: {t['outdated']}" for t in self.targets])
        self.data_queue.put({
            "propagation": {
                "target_count": target_count,
                "target_details": target_details
            }
        })
        print(f"Propagation targets found at {time.ctime()}: {target_count}")

    def find_potential_targets(self, current_data):
        targets = []
        try:
            arp_output = subprocess.check_output(["arp", "-n"], text=True)
            for line in arp_output.splitlines()[1:]:
                parts = line.split()
                if len(parts) >= 3:
                    ip = parts[0]
                    targets.append(self.score_target(ip, current_data))
        except subprocess.CalledProcessError as e:
            print(f"ARP scan error: {e}")
        return [t for t in targets if t["score"] > 0]

    def get_latest_data(self):
        latest = {}
        temp_queue = Queue()
        while not self.data_queue.empty():
            data = self.data_queue.get_nowait()
            temp_queue.put(data)
            latest.update(data)
        while not temp_queue.empty():
            self.data_queue.put(temp_queue.get_nowait())
        if not latest:
            print("No data found in queue for propagation")
        return latest

    def score_target(self, ip, current_data):
        score = 0
        outdated = []
        software_versions = current_data.get("program", {}).get("software_versions", "").splitlines()
        for line in software_versions:
            if ":" in line:
                try:
                    name, version = line.split(":", 1)
                    name = name.strip().lower()
                    version = version.strip()
                    latest = self.latest_versions.get(name)
                    if latest and version < latest:
                        outdated.append(f"{name}: {version} (Latest: {latest})")
                        score += 20
                except ValueError:
                    print(f"Failed to parse software version line: {line}")
                    continue
        system_data = current_data.get("system", {})
        if system_data.get("cpu_usage", 100) < 70:
            score += 20
        if system_data.get("memory_usage", 100) < 80:
            score += 20
        return {"ip": ip, "score": score, "outdated": ", ".join(outdated) if outdated else "None"}
