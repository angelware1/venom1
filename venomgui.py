import tkinter as tk
from tkinter import ttk
import time

class VenomGUI:
    def __init__(self, root, data_queue, state_queue):
        self.root = root
        self.data_queue = data_queue
        self.state_queue = state_queue
        self.data = {}
        self.states = {}
        self.last_process_update = 0
        self.setup_gui()
        self.update_gui()

    def setup_gui(self):
        self.root.title("Venom Metrics Monitor")
        self.root.geometry("1000x900")
        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=10, expand=True)
        tabs = ["System", "Network", "Program", "External", "Security", "History", "Additional", "Context", "Processes", "Propagation"]
        self.labels = {}
        self.process_tree = None
        self.program_text = None
        self.propagation_text = None

        for tab_name in tabs:
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=tab_name)
            self.labels[tab_name.lower()] = {}
            if tab_name.lower() == "processes":
                self.setup_process_tab(frame)
            elif tab_name.lower() == "program":
                self.setup_program_tab(frame)
            elif tab_name.lower() == "propagation":
                self.setup_propagation_tab(frame)
            else:
                self.create_labels(frame, tab_name.lower())

    def create_labels(self, frame, category):
        metrics = {
            "system": ["cpu_usage", "memory_usage", "disk_usage", "num_processes", "load_avg", "uptime", "battery_percent", "temperature", "cpu_freq_current", "cpu_freq_max", "swap_used", "swap_free", "swap_total", "boot_time", "fan_speeds", "disk_read_bytes_sec", "disk_write_bytes_sec", "disk_read_iops", "disk_write_iops", "memory_active", "memory_inactive", "memory_wired", "memory_cached", "page_faults", "swap_in_rate", "swap_out_rate", "interrupt_rate", "ctx_switch_rate", "thermal_zones", "battery_discharge_rate", "filesystems", "load_avg_1min", "load_avg_5min", "load_avg_15min", "total_threads"],
            "network": ["bandwidth", "latency", "traffic_volume", "sent_rate_mb", "recv_rate_mb", "active_connections", "packet_loss", "dns_resolution", "open_ports"],
            "external": ["time", "system_load", "geolocation", "wifi_networks"],
            "security": ["data_integrity"],
            "history": ["trends", "events"],
            "additional": ["running_processes", "file_changes"],
            "context": ["system_overall", "cpu_trend", "memory", "disk", "network_traffic", "connections", "packet_loss", "dns", "ports", "interfaces", "security", "bottleneck", "processes", "battery", "temperature", "uptime"]
        }.get(category, [])

        for i, metric in enumerate(metrics):
            label = ttk.Label(frame, text=f"{metric.replace('_', ' ').title()}: ")
            label.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            value_label = ttk.Label(frame, text="N/A", wraplength=600)
            value_label.grid(row=i, column=1, sticky="w", padx=5, pady=2)
            self.labels[category][metric] = value_label

    def setup_program_tab(self, frame):
        res_label = ttk.Label(frame, text="Resource Impact: ")
        res_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        res_value = ttk.Label(frame, text="N/A", wraplength=600)
        res_value.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        self.labels["program"]["resource_impact"] = res_value
        versions_label = ttk.Label(frame, text="Software Versions: ")
        versions_label.grid(row=1, column=0, sticky="nw", padx=5, pady=2)
        self.program_text = tk.Text(frame, height=20, width=80, wrap="none")
        self.program_text.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.program_text.yview)
        scrollbar.grid(row=1, column=2, sticky="ns", pady=2)
        self.program_text.configure(yscrollcommand=scrollbar.set)
        self.program_text.insert("end", "N/A")

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

    def setup_propagation_tab(self, frame):
        count_label = ttk.Label(frame, text="Target Count: ")
        count_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        count_value = ttk.Label(frame, text="0")
        count_value.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        self.labels["propagation"]["target_count"] = count_value
        details_label = ttk.Label(frame, text="Target Details: ")
        details_label.grid(row=1, column=0, sticky="nw", padx=5, pady=2)
        self.propagation_text = tk.Text(frame, height=20, width=80, wrap="none")
        self.propagation_text.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.propagation_text.yview)
        scrollbar.grid(row=1, column=2, sticky="ns", pady=2)
        self.propagation_text.configure(yscrollcommand=scrollbar.set)
        self.propagation_text.insert("end", "No targets detected yet")

    def update_gui(self):
        try:
            queue_had_data = False
            while not self.data_queue.empty():
                new_data = self.data_queue.get_nowait()
                print(f"Received from queue at {time.ctime()}: {new_data}")
                for category, metrics in new_data.items():
                    if category not in self.data:
                        self.data[category] = {}
                    self.data[category].update(metrics)
                    print(f"Merged into self.data[{category}]: {metrics}")
                queue_had_data = True

            if not queue_had_data:
                print("No new data in queue this cycle")

            if not self.state_queue.empty():
                self.states = self.state_queue.get_nowait()
                print(f"GUI retrieved states: {self.states.get('system_overall', 'N/A')}")

            if queue_had_data:  
                current_time = time.time()
                for category, metrics in self.labels.items():
                    if category == "context":
                        for metric, label in metrics.items():
                            value = self.states.get(metric, "N/A")
                            label.config(text=str(value))
                    elif category == "processes":
                        if self.process_tree and (current_time - self.last_process_update >= 5):
                            for item in self.process_tree.get_children():
                                self.process_tree.delete(item)
                            processes = self.data.get("system", {}).get("processes", [])
                            print(f"Updating processes tab with {len(processes)} entries")
                            sorted_procs = sorted(processes, key=lambda p: p.get("cpu_percent", 0), reverse=True)[:50]
                            for proc in sorted_procs:
                                self.process_tree.insert("", "end", values=(
                                    proc["pid"], proc["name"], f"{proc['cpu_percent']:.1f}",
                                    f"{proc['memory_percent']:.1f}", f"{proc['memory_used']:.2f}",
                                    proc["num_threads"], proc["open_files"], proc["create_time"],
                                    proc["status"], proc["username"]
                                ))
                            self.last_process_update = current_time
                    elif category == "program":
                        res_value = self.data.get("program", {}).get("resource_impact", "N/A")
                        self.labels["program"]["resource_impact"].config(text=str(res_value))
                        versions = self.data.get("program", {}).get("software_versions", "N/A")
                        print(f"Updating Program tab with software_versions: {versions[:50]}...")
                        self.program_text.delete("1.0", "end")
                        self.program_text.insert("end", versions)
                    elif category == "propagation":
                        count = self.data.get("propagation", {}).get("target_count", 0)
                        self.labels["propagation"]["target_count"].config(text=str(count))
                        details = self.data.get("propagation", {}).get("target_details", "No targets detected yet")
                        self.propagation_text.delete("1.0", "end")
                        self.propagation_text.insert("end", details)
                    else:
                        for metric, label in metrics.items():
                            value = self.data.get(category, {}).get(metric, "N/A")
                            if value is not None:
                                if isinstance(value, float):
                                    label.config(text=f"{value:.2f}")
                                elif isinstance(value, (dict, list)):
                                    label.config(text=str(value))
                                else:
                                    label.config(text=value)

        except Exception as e:
            print(f"GUI update error: {e}")
        self.root.after(1000, self.update_gui)
