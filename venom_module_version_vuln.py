import json
import time
import random

class PrivilegeEscalationEngine:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self.event_log = []

    def lookup_vulnerabilities(self, outdated_software, vuln_file="vulnlibrary.json"):
        vulnerabilities = []
        retries = 0
        while retries < self.max_retries:
            try:
                with open(vuln_file, "r") as f:
                    vuln_db = json.load(f)
                for software, installed, latest in outdated_software:
                    if software in vuln_db and installed in vuln_db[software]:
                        cve_list = vuln_db[software][installed]
                        vulnerabilities.append((software, installed, cve_list))
                        self.event_log.append(f"Vulnerabilities for {software} {installed}: {cve_list}")
                        print(f"Vulnerabilities for {software} {installed}: {cve_list}")
                break
            except Exception as e:
                retries += 1
                self.event_log.append(f"Error looking up vulnerabilities (attempt {retries}/{self.max_retries}): {e}")
                print(f"Error looking up vulnerabilities (attempt {retries}/{self.max_retries}): {e}")
                if retries < self.max_retries:
                    time.sleep(random.uniform(1, 5))
                else:
                    self.event_log.append("Max retries reached. Failed to lookup vulnerabilities.")
                    print("Max retries reached. Failed to lookup vulnerabilities.")
        return vulnerabilities

    def get_event_log(self):
        return self.event_log

if __name__ == "__main__":
    engine = PrivilegeEscalationEngine()
    # Example outdated software list from previous step
    outdated = [("apache", "2.4.50", "2.4.58"), ("kernel", "5.10", "5.15")]
    vulns = engine.lookup_vulnerabilities(outdated)
    print("\nVulnerabilities Found:", vulns if vulns else "None")
    print("\nEvent Log:")
    for entry in engine.get_event_log():
        print(entry)
