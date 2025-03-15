import psutil
import socket
import time
import asyncio
import os
import hashlib
from datetime import datetime

POLL_INTERVAL = 5
MONITOR_DIR = os.path.dirname(__file__)

class VenomDataGather:
    def __init__(self, data_queue):
        self.data = {
            "system": {},
            "network": {},
            "program": {},
            "external": {},
            "security": {},
            "history": {"trends": {}, "events": []},
            "additional": {}
        }
        self.data_queue = data_queue
        self.start_time = time.time()
        self.last_file_check = {f: os.stat(os.path.join(MONITOR_DIR, f)).st_mtime for f in os.listdir(MONITOR_DIR)}
        self.prev_sent = psutil.net_io_counters().bytes_sent
        self.prev_recv = psutil.net_io_counters().bytes_recv
        self.prev_time = time.time()
        self.prev_packets_sent = psutil.net_io_counters().packets_sent
        self.prev_packets_recv = psutil.net_io_counters().packets_recv
        self.prev_errout = psutil.net_io_counters().errout
        self.prev_errin = psutil.net_io_counters().errin
        # For deep metrics rate calculations
        self.prev_io = psutil.disk_io_counters()
        self.prev_io_time = time.time()
        self.prev_swap_io = psutil.swap_memory()
        self.prev_swap_io_time = time.time()
        self.prev_interrupts = psutil.cpu_stats().interrupts if hasattr(psutil.cpu_stats(), "interrupts") else 0
        self.prev_ctx_switches = psutil.cpu_stats().ctx_switches if hasattr(psutil.cpu_stats(), "ctx_switches") else 0

    async def run_once(self):
        self.start_time = time.time()
        self.gather_system_metrics()
        await self.gather_network_metrics()
        self.gather_program_metrics()
        self.gather_external_metrics()
        self.gather_security_metrics()
        self.update_historical_trends()
        self.gather_additional_metrics()
        # Calculate network rates and packet loss
        current_sent = psutil.net_io_counters().bytes_sent
        current_recv = psutil.net_io_counters().bytes_recv
        current_time = time.time()
        delta_time = current_time - self.prev_time
        if delta_time > 0:
            self.data["network"]["sent_rate_mb"] = (current_sent - self.prev_sent) / delta_time / 1024 / 1024
            self.data["network"]["recv_rate_mb"] = (current_recv - self.prev_recv) / delta_time / 1024 / 1024
            packets_sent = psutil.net_io_counters().packets_sent
            packets_recv = psutil.net_io_counters().packets_recv
            errout = psutil.net_io_counters().errout
            errin = psutil.net_io_counters().errin
            total_packets = (packets_sent - self.prev_packets_sent) + (packets_recv - self.prev_packets_recv)
            total_errors = (errout - self.prev_errout) + (errin - self.prev_errin)
            self.data["network"]["packet_loss"] = (total_errors / total_packets * 100) if total_packets > 0 else 0
        else:
            self.data["network"]["sent_rate_mb"] = 0
            self.data["network"]["recv_rate_mb"] = 0
            self.data["network"]["packet_loss"] = 0
        self.prev_sent = current_sent
        self.prev_recv = current_recv
        self.prev_time = current_time
        self.prev_packets_sent = psutil.net_io_counters().packets_sent
        self.prev_packets_recv = psutil.net_io_counters().packets_recv
        self.prev_errout = psutil.net_io_counters().errout
        self.prev_errin = psutil.net_io_counters().errin
        print(f"Data gathered: {self.data['system'].get('cpu_usage', 'N/A')} CPU%, queueing data")  # Debug print
        self.data_queue.put(self.data.copy())

    def gather_system_metrics(self):
        # Existing metrics
        self.data["system"]["cpu_usage"] = psutil.cpu_percent(interval=1)
        self.data["system"]["memory_usage"] = psutil.virtual_memory().percent
        self.data["system"]["disk_usage"] = psutil.disk_usage("/").percent
        self.data["system"]["num_processes"] = len(psutil.pids())
        self.data["system"]["load_avg"] = psutil.getloadavg()[0]
        self.data["system"]["uptime"] = time.time() - psutil.boot_time()
        battery = psutil.sensors_battery()
        if battery:
            self.data["system"]["battery_percent"] = battery.percent
            self.data["system"]["battery_plugged"] = battery.power_plugged
        else:
            self.data["system"]["battery_percent"] = None
            self.data["system"]["battery_plugged"] = None
        temperatures = psutil.sensors_temperatures()
        self.data["system"]["temperature"] = temperatures.get("coretemp", [{}])[0].get("current", None) if temperatures else None
        cpu_freq = psutil.cpu_freq()
        self.data["system"]["cpu_freq_current"] = cpu_freq.current if cpu_freq else 0
        self.data["system"]["cpu_freq_max"] = cpu_freq.max if cpu_freq else 0
        self.data["system"]["per_core_cpu_usage"] = psutil.cpu_percent(percpu=True)
        swap = psutil.swap_memory()
        self.data["system"]["swap_used"] = swap.used / 1024 / 1024
        self.data["system"]["swap_free"] = swap.free / 1024 / 1024
        self.data["system"]["swap_total"] = swap.total / 1024 / 1024
        self.data["system"]["boot_time"] = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        fans = psutil.sensors_fans()
        self.data["system"]["fan_speeds"] = {name: [f.current for f in fan_list] for name, fan_list in fans.items()} if fans else {}

        # Expanded process list
        processes = []
        for proc in psutil.process_iter([
            'pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'username',
            'exe', 'cmdline', 'memory_info', 'num_threads', 'open_files', 'create_time', 'io_counters'
        ]):
            try:
                info = proc.info
                process_data = {
                    "pid": info["pid"],
                    "name": info["name"],
                    "cpu_percent": info["cpu_percent"],
                    "memory_percent": info["memory_percent"],
                    "status": info["status"],
                    "username": info["username"],
                    "exe_path": info["exe"] or "N/A",
                    "cmdline": " ".join(info["cmdline"]) if info["cmdline"] else "N/A",
                    "memory_used": info["memory_info"].rss / 1024 / 1024 if info["memory_info"] else 0,
                    "num_threads": info["num_threads"] or 0,
                    "open_files": len(info["open_files"]) if info["open_files"] else 0,
                    "create_time": datetime.fromtimestamp(info["create_time"]).strftime("%Y-%m-%d %H:%M:%S") if info["create_time"] else "N/A",
                    "io_read_bytes": info["io_counters"].read_bytes / 1024 / 1024 if info["io_counters"] else 0,
                    "io_write_bytes": info["io_counters"].write_bytes / 1024 / 1024 if info["io_counters"] else 0
                }
                processes.append(process_data)
            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                continue
        self.data["system"]["processes"] = processes

        # New deep system metrics
        # Disk I/O Details
        io = psutil.disk_io_counters()
        if io and self.prev_io:
            delta_time = time.time() - self.prev_io_time
            if delta_time > 0:
                self.data["system"]["disk_read_bytes_sec"] = (io.read_bytes - self.prev_io.read_bytes) / delta_time / 1024 / 1024  # MB/s
                self.data["system"]["disk_write_bytes_sec"] = (io.write_bytes - self.prev_io.write_bytes) / delta_time / 1024 / 1024  # MB/s
                self.data["system"]["disk_read_iops"] = (io.read_count - self.prev_io.read_count) / delta_time
                self.data["system"]["disk_write_iops"] = (io.write_count - self.prev_io.write_count) / delta_time
            else:
                self.data["system"]["disk_read_bytes_sec"] = 0
                self.data["system"]["disk_write_bytes_sec"] = 0
                self.data["system"]["disk_read_iops"] = 0
                self.data["system"]["disk_write_iops"] = 0
        else:
            self.data["system"]["disk_read_bytes_sec"] = 0
            self.data["system"][" chia"] = 0
            self.data["system"]["disk_read_iops"] = 0
            self.data["system"]["disk_write_iops"] = 0
        self.prev_io = io
        self.prev_io_time = time.time()

        # Memory Details
        vm = psutil.virtual_memory()
        self.data["system"]["memory_active"] = vm.active / 1024 / 1024  # MB
        self.data["system"]["memory_inactive"] = vm.inactive / 1024 / 1024  # MB
        self.data["system"]["memory_wired"] = getattr(vm, "wired", 0) / 1024 / 1024  # MB, if available
        self.data["system"]["memory_cached"] = getattr(vm, "cached", 0) / 1024 / 1024  # MB, if available
        self.data["system"]["page_faults"] = psutil.cpu_stats().soft_interrupts if hasattr(psutil.cpu_stats(), "soft_interrupts") else 0  # Approximation
        if self.prev_swap_io and delta_time > 0:
            self.data["system"]["swap_in_rate"] = (swap.sin - self.prev_swap_io.sin) / delta_time  # Pages in/sec
            self.data["system"]["swap_out_rate"] = (swap.sout - self.prev_swap_io.sout) / delta_time  # Pages out/sec
        else:
            self.data["system"]["swap_in_rate"] = 0
            self.data["system"]["swap_out_rate"] = 0
        self.prev_swap_io = swap
        self.prev_swap_io_time = time.time()

        # System Interrupts and Context Switches
        cpu_stats = psutil.cpu_stats()
        if hasattr(cpu_stats, "interrupts") and self.prev_interrupts:
            self.data["system"]["interrupt_rate"] = (cpu_stats.interrupts - self.prev_interrupts) / delta_time
        else:
            self.data["system"]["interrupt_rate"] = 0
        self.prev_interrupts = cpu_stats.interrupts if hasattr(cpu_stats, "interrupts") else 0
        if hasattr(cpu_stats, "ctx_switches") and self.prev_ctx_switches:
            self.data["system"]["ctx_switch_rate"] = (cpu_stats.ctx_switches - self.prev_ctx_switches) / delta_time
        else:
            self.data["system"]["ctx_switch_rate"] = 0
        self.prev_ctx_switches = cpu_stats.ctx_switches if hasattr(cpu_stats, "ctx_switches") else 0

        # Thermal Zones
        self.data["system"]["thermal_zones"] = {name: [t.current for t in temps] for name, temps in temperatures.items()} if temperatures else {}

        # Power Consumption
        if battery and not battery.power_plugged and hasattr(battery, "secsleft"):
            self.data["system"]["battery_discharge_rate"] = (100 - battery.percent) / (battery.secsleft / 3600) if battery.secsleft > 0 else 0  # %/hour
        else:
            self.data["system"]["battery_discharge_rate"] = None

        # Filesystem Stats
        self.data["system"]["filesystems"] = []
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                self.data["system"]["filesystems"].append({
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total": usage.total / 1024 / 1024,  # MB
                    "used": usage.used / 1024 / 1024,    # MB
                    "free": usage.free / 1024 / 1024     # MB
                })
            except Exception:
                continue

        # System Load Details
        load1, load5, load15 = psutil.getloadavg()
        num_cores = psutil.cpu_count()
        self.data["system"]["load_avg_1min"] = load1 / num_cores  # Normalized
        self.data["system"]["load_avg_5min"] = load5 / num_cores
        self.data["system"]["load_avg_15min"] = load15 / num_cores

        # Kernel Metrics
        self.data["system"]["total_threads"] = sum(p.num_threads() or 0 for p in psutil.process_iter(['num_threads']))  # Fixed: Call num_threads()

    async def gather_network_metrics(self):
        io_counters = psutil.net_io_counters()
        self.data["network"]["bandwidth"] = io_counters.bytes_sent + io_counters.bytes_recv
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            start = time.time()
            s.connect(("8.8.8.8", 53))
            latency = (time.time() - start) * 1000
            s.close()
            self.data["network"]["latency"] = latency
        except Exception:
            self.data["network"]["latency"] = -1
        self.data["network"]["traffic_volume"] = io_counters.bytes_recv
        connections = []
        for conn in psutil.net_connections():
            connections.append({
                "local_addr": conn.laddr,
                "remote_addr": conn.raddr if conn.raddr else None,
                "status": conn.status,
                "type": "TCP" if conn.type == socket.SOCK_STREAM else "UDP"
            })
        self.data["network"]["active_connections"] = len(connections)
        self.data["network"]["connection_details"] = connections
        open_ports = [conn.laddr.port for conn in psutil.net_connections(kind="inet") if conn.status == "LISTEN"]
        self.data["network"]["open_ports"] = open_ports
        interfaces = {}
        for nic, stats in psutil.net_if_stats().items():
            io = psutil.net_io_counters(pernic=True).get(nic, None)
            interfaces[nic] = {
                "up": stats.isup,
                "speed": stats.speed,
                "bytes_sent": io.bytes_sent if io else 0,
                "bytes_recv": io.bytes_recv if io else 0
            }
        self.data["network"]["interfaces"] = interfaces
        try:
            start = time.time()
            socket.gethostbyname("google.com")
            self.data["network"]["dns_resolution"] = (time.time() - start) * 1000  # ms
        except Exception:
            self.data["network"]["dns_resolution"] = -1

    def gather_program_metrics(self):
        self.data["program"]["resource_impact"] = self.data["system"]["cpu_usage"] + self.data["system"]["memory_usage"]

    def gather_external_metrics(self):
        self.data["external"]["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.data["external"]["system_load"] = psutil.getloadavg()[0] if hasattr(psutil, "getloadavg") else "N/A"

    def gather_security_metrics(self):
        self.data["security"]["data_integrity"] = hashlib.md5(str(self.data).encode()).hexdigest()

    def update_historical_trends(self):
        self.data["history"]["trends"]["cpu_usage"] = self.data["system"]["cpu_usage"]
        self.data["history"]["events"].append(f"Data gathered at {self.data['external']['time']}")

    def gather_additional_metrics(self):
        self.data["additional"]["running_processes"] = len(psutil.pids())
        changes = []
        current_files = {f: os.stat(os.path.join(MONITOR_DIR, f)).st_mtime for f in os.listdir(MONITOR_DIR)}
        for f in current_files:
            if f in self.last_file_check and current_files[f] != self.last_file_check[f]:
                changes.append(f"Change in {f}")
        self.data["additional"]["file_changes"] = changes if changes else ["No changes"]
        self.last_file_check = current_files
