import psutil

class VenomContextEngine:
    def __init__(self, data_queue, state_queue):
        self.data_queue = data_queue
        self.state_queue = state_queue
        self.prev_data = None

    def run_once(self):
        try:
            if not self.data_queue.empty():
                raw_data = self.data_queue.get_nowait()
                state = self.process(raw_data)
                self.state_queue.put(state)
                self.data_queue.put(raw_data)
                self.prev_data = raw_data 
        except Exception as e:
            print(f"Context error: {e}")

    def process(self, raw_data):
        state = {}

        
        cpu_usage = raw_data["system"]["cpu_usage"]
        memory_usage = raw_data["system"]["memory_usage"]
        load_avg = raw_data["system"]["load_avg"]
        num_cores = psutil.cpu_count()
        if cpu_usage > 80 and memory_usage > 80 and load_avg > num_cores:
            state["system_overall"] = "heavy_load"
        elif cpu_usage > 80 or memory_usage > 80:
            state["system_overall"] = "stressed"
        elif cpu_usage < 20 and memory_usage < 20:
            state["system_overall"] = "idle"
        else:
            state["system_overall"] = "balanced"

       
        if self.prev_data and "cpu_usage" in self.prev_data["system"]:
            cpu_change = cpu_usage - self.prev_data["system"]["cpu_usage"]
            if cpu_change > 20:
                state["cpu_trend"] = "spiking"
            elif cpu_change < -20:
                state["cpu_trend"] = "dropping"
            else:
                state["cpu_trend"] = "stable"
        else:
            state["cpu_trend"] = "unknown"

        
        if memory_usage > 90:
            state["memory"] = "critical"
        elif memory_usage > 80:
            state["memory"] = "high"
        elif memory_usage < 20:
            state["memory"] = "low"
        else:
            state["memory"] = "normal"

        
        disk_usage = raw_data["system"]["disk_usage"]
        if disk_usage > 90 and cpu_usage < 50 and memory_usage < 50:
            state["disk"] = "io_bottleneck"
        elif disk_usage > 90:
            state["disk"] = "almost_full"
        else:
            state["disk"] = "normal"

       
        sent_rate = raw_data["network"].get("sent_rate_mb", 0)
        recv_rate = raw_data["network"].get("recv_rate_mb", 0)
        if sent_rate > 20 and recv_rate > 20:
            state["network_traffic"] = "congested"
        elif sent_rate > 10:
            state["network_traffic"] = "upload_heavy"
        elif recv_rate > 10:
            state["network_traffic"] = "download_heavy"
        else:
            state["network_traffic"] = "normal"

        
        active_connections = raw_data["network"]["active_connections"]
        connection_details = raw_data["network"]["connection_details"]
        unique_remotes = len(set(conn["remote_addr"][0] for conn in connection_details if conn["remote_addr"]))
        if active_connections > 50 and unique_remotes > 20:
            state["connections"] = "possible_scan"
        elif active_connections > 50:
            state["connections"] = "busy"
        else:
            state["connections"] = "quiet"

        
        packet_loss = raw_data["network"]["packet_loss"]
        if packet_loss > 5:
            state["packet_loss"] = "severe"
        elif packet_loss > 1:
            state["packet_loss"] = "high"
        else:
            state["packet_loss"] = "normal"

        
        dns_resolution = raw_data["network"]["dns_resolution"]
        if dns_resolution > 200 or dns_resolution == -1:
            state["dns"] = "failing"
        elif dns_resolution > 100:
            state["dns"] = "slow"
        else:
            state["dns"] = "fast"

        
        open_ports = len(raw_data["network"]["open_ports"])
        if open_ports > 20:
            state["ports"] = "highly_exposed"
        elif open_ports > 10:
            state["ports"] = "exposed"
        else:
            state["ports"] = "secure"

        
        interfaces = raw_data["network"]["interfaces"]
        any_down = any(not stats["up"] for stats in interfaces.values())
        total_bytes = sum(stats["bytes_sent"] + stats["bytes_recv"] for stats in interfaces.values())
        if any_down and total_bytes > 0:
            state["interfaces"] = "partial_failure"
        elif any_down:
            state["interfaces"] = "issues"
        else:
            state["interfaces"] = "stable"

        
        file_changes = raw_data["additional"]["file_changes"]
        if file_changes != ["No changes"] and unique_remotes > 10:
            state["security"] = "suspicious_activity"
        elif file_changes != ["No changes"]:
            state["security"] = "file_modifications"
        else:
            state["security"] = "secure"

        
        if cpu_usage > 80 and memory_usage < 50 and disk_usage < 50:
            state["bottleneck"] = "cpu_limited"
        elif memory_usage > 80 and cpu_usage < 50 and disk_usage < 50:
            state["bottleneck"] = "memory_limited"
        elif disk_usage > 90 and cpu_usage < 50 and memory_usage < 50:
            state["bottleneck"] = "disk_limited"
        else:
            state["bottleneck"] = "none"

       
        num_processes = raw_data["system"]["num_processes"]
        if num_processes > 200:
            state["processes"] = "overloaded"
        elif num_processes > 100:
            state["processes"] = "many"
        else:
            state["processes"] = "normal"

        
        battery_percent = raw_data["system"].get("battery_percent")
        if battery_percent is not None:
            if battery_percent < 10:
                state["battery"] = "critical"
            elif battery_percent < 20:
                state["battery"] = "low"
            elif raw_data["system"].get("battery_plugged"):
                state["battery"] = "charging"
            elif battery_percent > 90:
                state["battery"] = "full"
            else:
                state["battery"] = "normal"
        else:
            state["battery"] = "N/A"

        
        temperature = raw_data["system"].get("temperature")
        if temperature is not None:
            if temperature > 85:
                state["temperature"] = "critical"
            elif temperature > 70:
                state["temperature"] = "high"
            else:
                state["temperature"] = "normal"
        else:
            state["temperature"] = "N/A"

        
        uptime = raw_data["system"]["uptime"]
        if uptime > 604800:  
            state["uptime"] = "very_long"
        elif uptime > 86400:  
            state["uptime"] = "long"
        else:
            state["uptime"] = "short"

        return state
