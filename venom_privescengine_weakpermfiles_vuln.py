import os
import stat
import time
import random

class FilePermissionsExploitationModule:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self.event_log = []

    def check_weak_permissions(self):
        print("Checking for weak file/directory permissions...")
        # Critical paths to check (Linux focus)
        paths = [
            "/etc/passwd",  # Writable passwd can add a new root user
            "/etc/sudoers",  # Writable sudoers can grant sudo access
            "/root/.bashrc",  # Writable .bashrc can inject malicious commands
            "/bin/ping"      # Example SUID binary (often root-owned)
        ]
        exploits = []
        retries = 0
        while retries < self.max_retries:
            try:
                for path in paths:
                    if os.path.exists(path):
                        # Check if the path is writable by the current user
                        if os.access(path, os.W_OK):
                            exploits.append((path, "writable"))
                            self.event_log.append(f"Found writable path: {path}")
                            print(f"Found writable path: {path}")
                            # Check if it's an SUID binary owned by root
                            mode = os.stat(path).st_mode
                            if path == "/bin/ping" and (mode & stat.S_ISUID) and os.stat(path).st_uid == 0:
                                exploits.append((path, "SUID writable"))
                                self.event_log.append(f"Found root-owned SUID writable binary: {path}")
                                print(f"Found root-owned SUID writable binary: {path}")
                            # Exploitation notes
                            if path in ["/etc/passwd", "/etc/sudoers"]:
                                self.event_log.append(f"Exploit possible: Modify {path} to add privileged user")
                                print(f"Exploit possible: Modify {path} to add privileged user")
                            elif path == "/root/.bashrc":
                                self.event_log.append(f"Exploit possible: Inject malicious command into {path}")
                                print(f"Exploit possible: Inject malicious command into {path}")
                            elif "SUID" in exploits[-1][1]:
                                self.event_log.append(f"Exploit possible: Overwrite {path} with malicious script")
                                print(f"Exploit possible: Overwrite {path} with malicious script")
                break
            except Exception as e:
                retries += 1
                self.event_log.append(f"Error checking permissions (attempt {retries}/{self.max_retries}): {e}")
                print(f"Error checking permissions (attempt {retries}/{self.max_retries}): {e}")
                if retries < self.max_retries:
                    time.sleep(random.uniform(1, 5))
                else:
                    self.event_log.append("Max retries reached. Failed to check permissions.")
                    print("Max retries reached. Failed to check permissions.")
        return exploits

    def get_event_log(self):
        return self.event_log

if __name__ == "__main__":
    module = FilePermissionsExploitationModule()
    exploits = module.check_weak_permissions()
    print("\nExploitable Paths:", exploits if exploits else "None")
    print("\nEvent Log:")
    for entry in module.get_event_log():
        print(entry)
