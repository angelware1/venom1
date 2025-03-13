import asyncio
import threading
from venomdatagather import VenomDataGather
from venomgui import start_gui
from venomcontext import VenomContextEngine
# Comment out imports for modules that don’t exist yet
# from venomgoals import VenomGoalModule
# from venomoptions import VenomOptionModule
# from venomexecution import VenomExecutionModule
# from venomreflection import VenomReflectionModule

async def main():
    
    data_queue = asyncio.Queue()
    state_queue = asyncio.Queue()
    data_gatherer = VenomDataGather(data_queue)
    context = VenomContextEngine(data_queue, state_queue)

    
    gui_thread = threading.Thread(target=start_gui, args=(data_queue, state_queue), daemon=True)
    gui_thread.start()

    
    def run_context_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(context.run())

    context_thread = threading.Thread(target=run_context_loop, daemon=True)
    context_thread.start()

    
    while True:
        
        await data_gatherer.run_once()  

        # Uncomment for debugging
        # raw_data = await data_queue.get()
        # print(f"Collected data: {raw_data}")
        # await data_queue.put(raw_data)
        # print(f"Data queue size: {data_queue.qsize()}, State queue size: {state_queue.qsize()}")

        await asyncio.sleep(5)  

if __name__ == "__main__":
    asyncio.run(main())
