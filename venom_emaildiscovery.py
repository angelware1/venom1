import os
import time
import random

class EmailPropagationModule:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self.event_log = []

    def detect_email_software(self):
        email_software = []
        paths = {
            "Thunderbird": os.path.expanduser("~/.thunderbird"),
            "Outlook": os.path.expanduser("~/AppData/Local/Microsoft/Outlook")
        }
        retries = 0
        while retries < self.max_retries:
            try:
                for software, path in paths.items():
                    if os.path.exists(path):
                        email_software.append(software)
                        self.event_log.append(f"Detected {software} at {path}")
                        print(f"Detected {software} at {path}")
                break
            except Exception as e:
                retries += 1
                self.event_log.append(f"Error detecting email software (attempt {retries}/{self.max_retries}): {e}")
                print(f"Error detecting email software (attempt {retries}/{self.max_retries}): {e}")
                if retries < self.max_retries:
                    time.sleep(random.uniform(1, 5))
                else:
                    self.event_log.append("Max retries reached. Failed to detect email software.")
                    print("Max retries reached. Failed to detect email software.")
        return email_software

    def get_event_log(self):
        return self.event_log

if __name__ == "__main__":
    email_module = EmailPropagationModule()
    software = email_module.detect_email_software()
    print("\nDetected Email Software:", software if software else "None")
    print("\nEvent Log:")
    for entry in email_module.get_event_log():
        print(entry)
