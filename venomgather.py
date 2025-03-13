import psutil
import socket
import time
import asyncio
import threading
import os
import hashlib
from datetime import datetime


POLL_INTERVAL = 1  
MONITOR_DIR = os.path.dirname(__file__)  

class VenomDataGather:
    def __init__(self, data_queue):
        self.data = {
            "system": {},
            "network": {},
            "program": {},
            "external": {},
            "peer": {},
            "security": {},
            "application": {},
            "history": {"trends": {}, "events": []},
            "additional": {}
        }
        self.data_queue = data_queue
        self.start_time = time.time()
        self.last_file_check = {f: os.stat(os.path.join(MONITOR_DIR, f)).st_mtime for f in os.listdir(MONITOR_DIR)}

    def gather_system_metrics(self):
        self.data["system"]["cpu_usage"] = psutil.cpu_percent(interval=1)
        self.data["system"]["memory_usage"] = psutil.virtual_memory().percent
        self.data["system"]["disk_usage"] = psutil.disk_usage('/').percent
        self.data["system"]["process_status"] = {
            "threads": threading.active_count(),
            "uptime": time.time() - psutil.boot_time()
        }
        self.data["system"]["power_consumption"] = psutil.sensors_battery().percent if psutil.sensors_battery() else None
        self.data["system"]["temperature"] = psutil.sensors_temperatures().get('coretemp', [None])[0].current if psutil.sensors_temperatures() else None
        self.data["system"]["execution_time"] = time.time() - self.start_time

    async def gather_network_metrics(self):
        io_counters = psutil.net_io_counters()
        self.data["network"]["bandwidth"] = io_counters.bytes_sent + io_counters.bytes_recv
        try:
            start = time.time()
            socket.create_connection(("8.8.8.8", 53), timeout=2).close()
            self.data["network"]["latency"] = (time.time() - start) * 1000  # ms
        except Exception:
            self.data["network"]["latency"] = -1
        self.data["network"]["connected_devices"] = len(psutil.net_connections())
        self.data["network"]["traffic_volume"] = io_counters.bytes_sent
        self.data["network"]["open_ports"] = [conn.laddr.port for conn in psutil.net_connections() if conn.status == "LISTEN"]
        interfaces = {}
        for nic, stats in psutil.net_if_stats().items():
            interfaces[nic] = {"up": stats.isup, "speed": stats.speed}
        self.data["network"]["interfaces"] = interfaces
        per_nic = psutil.net_io_counters(pernic=True)
        self.data["network"]["packet_stats"] = {
            nic: {"packets_sent": stats.packets_sent, "packets_recv": stats.packets_recv, "errin": stats.errin}
            for nic, stats in per_nic.items()
        }

    def gather_program_metrics(self):
        self.data["program"]["resource_impact"] = {
            "cpu_change": psutil.cpu_percent(interval=1) - self.data["system"]["cpu_usage"]
        }

    def gather_external_metrics(self):
        self.data["external"]["time"] = datetime.now().isoformat()
        self.data["external"]["system_load"] = psutil.getloadavg()[0]

    def gather_security_metrics(self):
        with open(__file__, "rb") as f:
            self.data["security"]["data_integrity"] = hashlib.sha256(f.read()).hexdigest()

    def gather_application_metrics(self):
        pass

    def update_historical_trends(self):
        timestamp = self.data["external"]["time"]
        self.data["history"]["trends"]["cpu"] = self.data["history"]["trends"].get("cpu", []) + [(timestamp, self.data["system"]["cpu_usage"])]
        self.data["history"]["trends"]["cpu"] = self.data["history"]["trends"]["cpu"][-100:]
        self.data["history"]["events"].append({"time": timestamp, "event": "data_gathered"})

    def gather_additional_metrics(self):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            processes.append({
                "pid": proc.info['pid'],
                "name": proc.info['name'],
                "cpu": proc.info['cpu_percent'],
                "memory": proc.info['memory_info'].rss / 1024 / 1024  # MB
            })
        self.data["additional"]["running_processes"] = processes[:5]
        changes = []
        current_files = {f: os.stat(os.path.join(MONITOR_DIR, f)).st_mtime for f in os.listdir(MONITOR_DIR)}
        for fname, mtime in current_files.items():
            if fname in self.last_file_check and mtime != self.last_file_check[fname]:
                changes.append(f"{fname} modified")
        self.last_file_check = current_files
        self.data["additional"]["file_changes"] = changes if changes else ["No changes"]

    async def run_once(self):
        self.start_time = time.time()
        self.gather_system_metrics()
        await self.gather_network_metrics()
        self.gather_program_metrics()
        self.gather_external_metrics()
        self.gather_security_metrics()
        self.gather_application_metrics()
        self.update_historical_trends()
        self.gather_additional_metrics()
        await self.data_queue.put(self.data.copy())  
