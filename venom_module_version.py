import json
import time
import random

class PrivilegeEscalationEngine:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self.event_log = []

    def check_outdated_software(self, version_file="versiondata.json"):
        outdated_software = []
        # Hardcoded up-to-date versions (minimal for lightweight design)
        latest_versions = {
            "kernel": "5.15",  # Example: Linux kernel
            "apache": "2.4.58",
            "nginx": "1.26.0",
            "mysql": "8.0.35",
            "python": "3.12.0"
        }
        retries = 0
        while retries < self.max_retries:
            try:
                with open(version_file, "r") as f:
                    installed_versions = json.load(f)  # Read versiondata.json
                for software, installed in installed_versions.items():
                    if software in latest_versions:
                        latest = latest_versions[software]
                        if installed < latest:  # Simple string comparison for versions
                            outdated_software.append((software, installed, latest))
                            self.event_log.append(f"Outdated: {software} (Installed: {installed}, Latest: {latest})")
                            print(f"Outdated: {software} (Installed: {installed}, Latest: {latest})")
                break
            except Exception as e:
                retries += 1
                self.event_log.append(f"Error checking versions (attempt {retries}/{self.max_retries}): {e}")
                print(f"Error checking versions (attempt {retries}/{self.max_retries}): {e}")
                if retries < self.max_retries:
                    time.sleep(random.uniform(1, 5))
                else:
                    self.event_log.append("Max retries reached. Failed to check versions.")
                    print("Max retries reached. Failed to check versions.")
        return outdated_software

    def get_event_log(self):
        return self.event_log

if __name__ == "__main__":
    engine = PrivilegeEscalationEngine()
    outdated = engine.check_outdated_software()
    print("\nOutdated Software:", outdated if outdated else "None")
    print("\nEvent Log:")
    for entry in engine.get_event_log():
        print(entry)
