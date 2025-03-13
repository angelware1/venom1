import asyncio

class VenomContextEngine:
    def __init__(self, data_queue, state_queue):
        self.data_queue = data_queue
        self.state_queue = state_queue

    async def run(self):
        while True:
            try:
                if not self.data_queue.empty():
                    raw_data = await self.data_queue.get()
                    state = self.process(raw_data)
                    await self.state_queue.put(state)
                    
                    await self.data_queue.put(raw_data)
            except Exception as e:
                print(f"Context error: {e}")
            await asyncio.sleep(1)  

    def process(self, raw_data):
        state = {}

        
        cpu_usage = raw_data.get("system", {}).get("cpu_usage", 0)
        if cpu_usage > 80:
            state["system"] = "overloaded"
        elif cpu_usage < 20:
            state["system"] = "idle"
        else:
            state["system"] = "normal"

        
        latency = raw_data.get("network", {}).get("latency", -1)
        connected_devices = raw_data.get("network", {}).get("connected_devices", 0)
        if latency == -1 or latency > 100:  
            state["network"] = "unstable"
        elif connected_devices > 50:  
            state["network"] = "crowded"
        else:
            state["network"] = "stable"

        
        file_changes = raw_data.get("additional", {}).get("file_changes", ["No changes"])
        if file_changes != ["No changes"]:
            state["security"] = "threat_detected"
        else:
            state["security"] = "secure"

        return state
