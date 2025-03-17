import asyncio
import tkinter as tk
from queue import Queue
import threading
import time 
from venomdatagather import VenomDataGather
from venomcontext import VenomContextEngine
from venomgui import VenomGUI
from venomgeolocation import VenomGeolocation
from venomwificheck import VenomWifiCheck
from venomversioncheck import VenomVersionCheck
from venompropagation import VenomPropagation

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
    async_thread = threading.Thread(target=run_async_loop, args=(data_gather, context_engine, geo, wifi, version, propagation), daemon=True)
    async_thread.start()
    root.mainloop()
