import os
import time
import random
import stat

class ServiceMisconfigModule:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self.event_log = []

    def exploit_service_misconfig(self):
        print("Checking for service misconfigurations...")
        # Common service paths to check (Linux focus)
        service_paths = [
            "/etc/systemd/system/multi-user.target.wants/sshd.service",  # SSH service
            "/etc/systemd/system/multi-user.target.wants/nginx.service",  # Nginx service
        ]
        exploits = []
        retries = 0
        while retries < self.max_retries:
            try:
                for service_path in service_paths:
                    if os.path.exists(service_path):
                        # Check if the service file is writable by the current user
                        if os.access(service_path, os.W_OK):
                            with open(service_path, "r") as f:
                                content = f.read()
                            # Look for the binary path in the service file
                            for line in content.splitlines():
                                if line.startswith("ExecStart="):
                                    binary_path = line.split("=", 1)[1].split()[0]
                                    # Check if the binary is writable
                                    if os.path.exists(binary_path) and os.access(binary_path, os.W_OK):
                                        exploits.append((service_path, binary_path))
                                        self.event_log.append(f"Found writable service: {service_path} (Binary: {binary_path})")
                                        print(f"Found writable service: {service_path} (Binary: {binary_path})")
                                        # Simulate exploit by overwriting the binary (in a real scenario, replace with malicious payload)
                                        self.event_log.append(f"Exploit possible: Overwrite {binary_path} with malicious payload")
                                        print(f"Exploit possible: Overwrite {binary_path} with malicious payload")
                break
            except Exception as e:
                retries += 1
                self.event_log.append(f"Error checking services (attempt {retries}/{self.max_retries}): {e}")
                print(f"Error checking services (attempt {retries}/{self.max_retries}): {e}")
                if retries < self.max_retries:
                    time.sleep(random.uniform(1, 5))
                else:
                    self.event_log.append("Max retries reached. Failed to check services.")
                    print("Max retries reached. Failed to check services.")
        return exploits

    def get_event_log(self):
        return self.event_log

if __name__ == "__main__":
    module = ServiceMisconfigModule()
    exploits = module.exploit_service_misconfig()
    print("\nExploitable Services:", exploits if exploits else "None")
    print("\nEvent Log:")
    for entry in module.get_event_log():
        print(entry)
