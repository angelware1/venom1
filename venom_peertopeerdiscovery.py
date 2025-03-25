from scapy.all import ARP, Ether, srp
import netifaces
import sys
import time
import random

class LightweightP2PNetworkDiscovery:
    def __init__(self, network_cidr=None, max_retries=5, retry_delay_min=1, retry_delay_max=5):
        """
        Initialize the lightweight P2P Network Discovery Module with robust retry and self-healing.
        
        Args:
            network_cidr (str): The network range to scan (e.g., "192.168.1.0/24"). If None, auto-detects.
            max_retries (int): Maximum number of retries for failed scans.
            retry_delay_min (float): Minimum delay between retries (seconds).
            retry_delay_max (float): Maximum delay between retries (seconds).
        """
        self.network_cidr = network_cidr if network_cidr else self.detect_network_cidr()
        self.max_retries = max_retries
        self.retry_delay_min = retry_delay_min
        self.retry_delay_max = retry_delay_max
        self.discovered_devices = []
        self.event_log = []  # For tracking actions and errors (Issue Detection)

    def detect_network_cidr(self):
        """Automatically detect the network CIDR range of the host."""
        try:
            interfaces = netifaces.interfaces()
            for iface in interfaces:
                addrs = netifaces.ifaddresses(iface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        ip = addr.get("addr")
                        netmask = addr.get("netmask")
                        if ip and netmask and ip != "127.0.0.1":
                            ip_parts = list(map(int, ip.split(".")))
                            mask_parts = list(map(int, netmask.split(".")))
                            cidr_bits = sum(bin(x).count("1") for x in mask_parts)
                            network = ".".join(map(str, [ip_parts[i] & mask_parts[i] for i in range(4)]))
                            return f"{network}/{cidr_bits}"
            self.event_log.append("Warning: Could not detect network range. Using default 192.168.1.0/24.")
            return "192.168.1.0/24"
        except Exception as e:
            self.event_log.append(f"Error detecting network range: {e}. Using default 192.168.1.0/24.")
            return "192.168.1.0/24"

    def discover_devices(self):
        """Discover devices on the local network using ARP scanning with robust retries."""
        print(f"Scanning network: {self.network_cidr}")
        retries = 0
        while retries < self.max_retries:
            try:
                # Create ARP request packet
                arp = ARP(pdst=self.network_cidr)
                ether = Ether(dst="ff:ff:ff:ff:ff:ff")
                packet = ether / arp

                # Send packet and receive responses
                result = srp(packet, timeout=2, verbose=0)[0]

                # Collect discovered devices
                for sent, received in result:
                    ip = received.psrc
                    mac = received.hwsrc
                    if ip not in [d["ip"] for d in self.discovered_devices]:
                        device = {"ip": ip, "mac": mac}
                        self.discovered_devices.append(device)
                        self.event_log.append(f"Discovered device: {ip} ({mac})")
                        print(f"Discovered device: {ip} ({mac})")
                return  # Exit on successful scan
            except PermissionError as e:
                self.event_log.append(f"Permission error: {e}. Please run with elevated privileges.")
                print(f"Permission error: {e}. Please run with elevated privileges.")
                sys.exit(1)
            except Exception as e:
                retries += 1
                self.event_log.append(f"Error during discovery (attempt {retries}/{self.max_retries}): {e}")
                print(f"Error during discovery (attempt {retries}/{self.max_retries}): {e}")
                if retries < self.max_retries:
                    # Self-healing: Random delay to avoid detection and allow network recovery
                    delay = random.uniform(self.retry_delay_min, self.retry_delay_max)
                    self.event_log.append(f"Retrying after {delay:.2f} seconds...")
                    print(f"Retrying after {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    self.event_log.append("Max retries reached. Discovery failed.")
                    print("Max retries reached. Discovery failed.")

    def get_discovered_devices(self):
        """Return the list of discovered devices."""
        return self.discovered_devices

    def get_event_log(self):
        """Return the event log for debugging and feedback."""
        return self.event_log

# Example usage
if __name__ == "__main__":
    # Initialize the discovery module with auto-detected network range
    discovery_module = LightweightP2PNetworkDiscovery(max_retries=5, retry_delay_min=1, retry_delay_max=5)

    # Perform network discovery
    discovery_module.discover_devices()

    # Print discovered devices
    devices = discovery_module.get_discovered_devices()
    if devices:
        print(f"\nTotal devices discovered: {len(devices)}")
    else:
        print("\nNo devices discovered.")

    # Print event log for debugging
    print("\nEvent Log:")
    for entry in discovery_module.get_event_log():
        print(entry)
