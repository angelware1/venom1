import tkinter as tk
from tkinter import ttk

class VenomGUI:
    def __init__(self, root, data_queue, state_queue):
        self.root = root
        self.data_queue = data_queue
        self.state_queue = state_queue
        self.data = {}
        self.states = {}
        self.setup_gui()
        self.update_gui()

    def setup_gui(self):
        self.root.title("Venom Metrics Monitor")
        self.root.geometry("1000x900")

        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=10, expand=True)

        tabs = ["System", "Network", "Program", "External", "Security", "History", "Additional", "Context", "Processes"]
        self.labels = {}
        self.process_tree = None

        for tab_name in tabs:
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=tab_name)
            self.labels[tab_name.lower()] = {}
            if tab_name.lower() == "processes":
                self.setup_process_tab(frame)
            else:
                self.create_labels(frame, tab_name.lower())

    def create_labels(self, frame, category):
        metrics = {
            "system": [
                "cpu_usage", "memory_usage", "disk_usage", "num_processes", "load_avg", "uptime", 
                "battery_percent", "temperature", "cpu_freq_current", "cpu_freq_max", 
                "swap_used", "swap_free", "swap_total", "boot_time", "fan_speeds",
                "disk_read_bytes_sec", "disk_write_bytes_sec", "disk_read_iops", "disk_write_iops",
                "memory_active", "memory_inactive", "memory_wired", "memory_cached", "page_faults",
                "swap_in_rate", "swap_out_rate", "interrupt_rate", "ctx_switch_rate",
                "thermal_zones", "battery_discharge_rate", "filesystems",
                "load_avg_1min", "load_avg_5min", "load_avg_15min", "total_threads"
            ],
            "network": ["bandwidth", "latency", "traffic_volume", "sent_rate_mb", "recv_rate_mb", "active_connections", "packet_loss", "dns_resolution", "open_ports"],
            "program": ["resource_impact"],
            "external": ["time", "system_load", "geolocation"],  # Added "geolocation" here
            "security": ["data_integrity"],
            "history": ["trends", "events"],
            "additional": ["running_processes", "file_changes"],
            "context": [
                "system_overall", "cpu_trend", "memory", "disk", "network_traffic", "connections",
                "packet_loss", "dns", "ports", "interfaces", "security", "bottleneck",
                "processes", "battery", "temperature", "uptime"
            ]
        }.get(category, [])

        for i, metric in enumerate(metrics):
            label = ttk.Label(frame, text=f"{metric.replace('_', ' ').title()}: ")
            label.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            value_label = ttk.Label(frame, text="N/A", wraplength=600)
            value_label.grid(row=i, column=1, sticky="w", padx=5, pady=2)
            self.labels[category][metric] = value_label

    def setup_process_tab(self, frame):
        columns = ("pid", "name", "cpu_percent", "memory_percent", "memory_used", "threads", "open_files", "create_time", "status", "username")
        self.process_tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)
        self.process_tree.pack(fill="both", expand=True, padx=5, pady=5)

        self.process_tree.heading("pid", text="PID")
        self.process_tree.heading("name", text="Name")
        self.process_tree.heading("cpu_percent", text="CPU %")
        self.process_tree.heading("memory_percent", text="Mem %")
        self.process_tree.heading("memory_used", text="Mem Used (MB)")
        self.process_tree.heading("threads", text="Threads")
        self.process_tree.heading("open_files", text="Open Files")
        self.process_tree.heading("create_time", text="Start Time")
        self.process_tree.heading("status", text="Status")
        self.process_tree.heading("username", text="User")

        self.process_tree.column("pid", width=60)
        self.process_tree.column("name", width=150)
        self.process_tree.column("cpu_percent", width=70)
        self.process_tree.column("memory_percent", width=70)
        self.process_tree.column("memory_used", width=90)
        self.process_tree.column("threads", width=60)
        self.process_tree.column("open_files", width=80)
        self.process_tree.column("create_time", width=120)
        self.process_tree.column("status", width=80)
        self.process_tree.column("username", width=100)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.process_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.process_tree.configure(yscrollcommand=scrollbar.set)

    def update_gui(self):
        try:
            if not self.data_queue.empty():
                self.data = self.data_queue.get_nowait()
                print(f"GUI retrieved data: {self.data['system'].get('cpu_usage', 'N/A')} CPU%")  # Debug print
            else:
                print("Data queue empty")  # Debug print
            if not self.state_queue.empty():
                self.states = self.state_queue.get_nowait()
                print(f"GUI retrieved states: {self.states.get('system_overall', 'N/A')}")  # Debug print

            for category, metrics in self.labels.items():
                if category == "context":
                    for metric, label in metrics.items():
                        value = self.states.get(metric, "N/A")
                        label.config(text=str(value))
                elif category == "processes":
                    if self.process_tree:
                        for item in self.process_tree.get_children():
                            self.process_tree.delete(item)
                        processes = self.data.get("system", {}).get("processes", [])
                        print(f"Updating processes tab with {len(processes)} entries")  # Debug print
                        for proc in processes:
                            self.process_tree.insert("", "end", values=(
                                proc["pid"],
                                proc["name"],
                                f"{proc['cpu_percent']:.1f}",
                                f"{proc['memory_percent']:.1f}",
                                f"{proc['memory_used']:.2f}",
                                proc["num_threads"],
                                proc["open_files"],
                                proc["create_time"],
                                proc["status"],
                                proc["username"]
                            ))
                elif category == "system":
                    for metric, label in metrics.items():
                        value = self.data.get(category, {}).get(metric)
                        if value is not None:
                            if metric == "filesystems":
                                fs_str = "\n".join([f"{fs['mountpoint']} ({fs['fstype']}): {fs['used']:.1f}/{fs['total']:.1f} MB" for fs in value])
                                label.config(text=fs_str or "N/A")
                            else:
                                label.config(text=str(value) if isinstance(value, (dict, list)) else f"{value:.2f}" if isinstance(value, float) else str(value))
                else:
                    for metric, label in metrics.items():
                        value = self.data.get(category, {}).get(metric)
                        if value is not None:
                            label.config(text=str(value) if isinstance(value, (dict, list)) else f"{value:.2f}" if isinstance(value, float) else str(value))
        except Exception as e:
            print(f"GUI update error: {e}")
        self.root.after(1000, self.update_gui)
