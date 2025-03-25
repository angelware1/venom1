import subprocess
import pkg_resources
import platform
import time

class VenomVersionCheck:
    def __init__(self, data_queue):
        self.data_queue = data_queue
        print("Venom Version Check initialized")

    async def run_once(self):
        versions = self.get_software_versions()
        self.data_queue.put({
            "program": {
                "software_versions": versions
            }
        })
        print(f"Software versions queued at {time.ctime()}: {versions[:100]}...")
        await asyncio.sleep(0)

    def get_software_versions(self):
        versions = [f"Timestamp: {time.ctime()}"] 
        os_info = platform.uname()
        try:
            with open("/etc/os-release") as f:
                os_release = {line.split("=")[0]: line.split("=")[1].strip().strip('"') for line in f if "=" in line}
            versions.append(f"OS: {os_release.get('PRETTY_NAME', 'Unknown')}")
        except FileNotFoundError:
            versions.append("OS: Unknown (no /etc/os-release)")
        versions.append(f"Kernel: {os_info.release}")
        try:
            dpkg_output = subprocess.check_output(["dpkg", "-l"], text=True)
            for line in dpkg_output.splitlines():
                if line.startswith("ii"):
                    parts = line.split()
                    versions.append(f"{parts[1]}: {parts[2]}")
        except subprocess.CalledProcessError as e:
            versions.append(f"DPKG Error: {e}")
        try:
            for dist in pkg_resources.working_set:
                versions.append(f"Python {dist.key}: {dist.version}")
        except Exception as e:
            versions.append(f"Python Modules Error: {e}")
        return "\n".join(versions)
