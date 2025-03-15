import asyncio
import tkinter as tk
from queue import Queue
import threading
from venomdatagather import VenomDataGather
from venomcontext import VenomContextEngine
from venomgui import VenomGUI
from venomgeolocation import VenomGeolocation

def run_async_loop(data_gather, context_engine, geo):
    async def inner_loop():
        while True:
            await data_gather.run_once()
            context_engine.run_once()
            await geo.run_once()
            await asyncio.sleep(5)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(inner_loop())

if __name__ == "__main__":
    data_queue = Queue()
    state_queue = Queue()
    data_gather = VenomDataGather(data_queue)
    context_engine = VenomContextEngine(data_queue, state_queue)
    geo = VenomGeolocation(data_queue)
    root = tk.Tk()
    gui = VenomGUI(root, data_queue, state_queue)
    async_thread = threading.Thread(target=run_async_loop, args=(data_gather, context_engine, geo), daemon=True)
    async_thread.start()
    root.mainloop()
