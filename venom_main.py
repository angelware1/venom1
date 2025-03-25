import asyncio
import tkinter as tk
from queue import Queue
import threading
import time
import os
from venomdatagather import VenomDataGather
from venomcontext import VenomContextEngine
from venomgui import VenomGUI
from venomgeolocation import VenomGeolocation
from venomwificheck import VenomWifiCheck
from venomversioncheck import VenomVersionCheck
from venompropagation import VenomPropagation
from venom_peertopeerdiscovery import SimpleNetworkDiscovery

def run_async_loop(data_gather, context_engine, geo, wifi, version, propagation):
    async def inner_loop():
        iteration = 0
        while True:
            print(f"Async loop iteration {iteration} starting at {time.ctime()}")
            try:
                await data_gather.run_once()
                print("DataGather completed")
                context_engine.run_once()
                print("ContextEngine completed")
                await geo.run_once()
                print("Geolocation completed")
                await wifi.run_once()
                print("WifiCheck completed")
                await version.run_once()
                print("VersionCheck completed")
                await propagation.run_once()
                print("Propagation completed")
            except Exception as e:
                print(f"Error in async loop iteration {iteration}: {e}")
            print(f"Async loop iteration {iteration} finished, sleeping for 5s")
            iteration += 1
            await asyncio.sleep(5)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(inner_loop())
    except Exception as e:
        print(f"Async loop crashed: {e}")

def setup_p2p_window(root):
    p2p_window = tk.Toplevel(root)
    p2p_window.title("Venom P2P Discovery")
    p2p_window.geometry("600x400")
    
    p2p_text = tk.Text(p2p_window, height=20, width=70)
    p2p_text.pack(padx=10, pady=10, fill="both", expand=True)
    
    scrollbar = tk.Scrollbar(p2p_window, command=p2p_text.yview)
    scrollbar.pack(side="right", fill="y")
    p2p_text.config(yscrollcommand=scrollbar.set)
    
    if os.geteuid() != 0:
        p2p_text.insert("end", "Warning: Run with sudo for best results (using ARP cache only).\n")
        print("P2P running without sudo—limited to ARP cache")
    else:
        print("P2P running with sudo—full scan possible")
    
    try:
        discovery = SimpleNetworkDiscovery()
        discovery.discover()
        devices, logs = discovery.get_results()
        
        p2p_text.insert("end", "Discovered Devices:\n")
        if devices:
            for device in devices:
                p2p_text.insert("end", f"IP: {device['ip']} | MAC: {device['mac']}\n")
            p2p_text.insert("end", f"\nTotal devices: {len(devices)}\n")
        else:
            p2p_text.insert("end", "No devices found.\n")
        
        p2p_text.insert("end", "\nEvent Log:\n")
        for log in logs:
            p2p_text.insert("end", f"{log}\n")
        print("P2P window setup complete")
    except Exception as e:
        p2p_text.insert("end", f"Error: {e}\n")
        print(f"P2P setup failed: {e}")

if __name__ == "__main__":
    data_queue = Queue()
    state_queue = Queue()
    data_gather = VenomDataGather(data_queue)
    context_engine = VenomContextEngine(data_queue, state_queue)
    geo = VenomGeolocation(data_queue)
    wifi = VenomWifiCheck(data_queue)
    version = VenomVersionCheck(data_queue)
    propagation = VenomPropagation(data_queue)
    
    root = tk.Tk()
    gui = VenomGUI(root, data_queue, state_queue)
    
    setup_p2p_window(root)
    
    async_thread = threading.Thread(target=run_async_loop, args=(data_gather, context_engine, geo, wifi, version, propagation), daemon=True)
    async_thread.start()
    
    root.mainloop()
