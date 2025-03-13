import tkinter as tk
from tkinter import ttk
import threading

def start_gui(data_queue, state_queue):
    root = tk.Tk()
    gui = VenomGUI(root, data_queue, state_queue)
    root.mainloop()

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
        self.root.title("Venom")
        self.root.geometry("800x900")

        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=10, expand=True)

        tabs = ["System", "Network", "Program", "External", "Security", "History", "Additional", "Context"]
        self.labels = {}
        for tab_name in tabs:
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=tab_name)
            self.labels[tab_name.lower()] = {}

        
        self.create_labels("system", ["cpu_usage", "memory_usage", "disk_usage", "process_status", "power_consumption", "temperature", "execution_time"])
        self.create_labels("network", ["bandwidth", "latency", "connected_devices", "traffic_volume", "open_ports", "interfaces", "packet_stats"])
        self.create_labels("program", ["resource_impact"])
        self.create_labels("external", ["time", "system_load"])
        self.create_labels("security", ["data_integrity"])
        self.create_labels("history", ["trends", "events"])
        self.create_labels("additional", ["running_processes", "file_changes"])
        self.create_labels("context", ["system", "network", "security"])  

    def create_labels(self, category, metrics):
        frame = self.root.winfo_children()[0].winfo_children()[list(self.labels.keys()).index(category)]
        for i, metric in enumerate(metrics):
            label = ttk.Label(frame, text=f"{metric.replace('_', ' ').title()}: ")
            label.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            value_label = ttk.Label(frame, text="N/A", wraplength=600)
            value_label.grid(row=i, column=1, sticky="w", padx=5, pady=2)
            self.labels[category][metric] = value_label

    def update_gui(self):
        try:
            
            if not self.data_queue.empty():
                self.data = self.data_queue.get_nowait()
            
            if not self.state_queue.empty():
                self.states = self.state_queue.get_nowait()

            
            for category, metrics in self.labels.items():
                if category == "context":
                    for metric, label in metrics.items():
                        value = self.states.get(metric, "N/A")
                        label.config(text=str(value))
                else:
                    for metric, label in metrics.items():
                        value = self.data.get(category, {}).get(metric)
                        if value is not None:
                            if isinstance(value, (dict, list)):
                                label.config(text=str(value))
                            else:
                                label.config(text=f"{value:.2f}" if isinstance(value, float) else str(value))
        except Exception:
            pass  
        self.root.after(1000, self.update_gui)
