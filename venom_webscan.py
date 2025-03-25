import argparse
import subprocess

# Function to get subdomains using Subfinder
def get_subdomains(url):
    try:
        result = subprocess.run(['subfinder', '-d', url], capture_output=True, text=True)
        subdomains = result.stdout.splitlines()
        return [s for s in subdomains if s]  # Filter out empty lines
    except FileNotFoundError:
        print("Error: Subfinder not found. Please install it (e.g., 'go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest').")
        return []

# Run Nmap scan with real-time output
def run_nmap_scan(subdomain):
    print(f"\n### Starting Nmap Scan for {subdomain} ###")
    process = subprocess.Popen(
        ['nmap', '-sV', '-p', '80,443', subdomain],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    # Print output in real-time
    for line in process.stdout:
        print(line, end='')
    process.wait()

# Run Nikto scan with real-time output
def run_nikto_scan(subdomain):
    print(f"\n### Starting Nikto Scan for {subdomain} ###")
    process = subprocess.Popen(
        ['nikto', '-h', subdomain, '-Tuning', '0123456789abcdex', '-nossl', '-timeout', '10', '-maxtime', '30', '-Display', 'V'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    # Print output in real-time
    for line in process.stdout:
        print(line, end='')
    process.wait()

# Main function
def main():
    parser = argparse.ArgumentParser(description="Subdomain Scanner with Nmap and Nikto")
    parser.add_argument('-u', '--url', type=str, required=True, help="Target URL (e.g., example.com)")
    args = parser.parse_args()

    # Step 1: Discover subdomains
    print(f"[+] Discovering subdomains for {args.url}")
    subdomains = get_subdomains(args.url)
    if not subdomains:
        print("No subdomains found or Subfinder failed.")
        return

    print("[+] Subdomains found:")
    for subdomain in subdomains:
        print(f"- {subdomain}")

    # Step 2: Run Nmap scans on all subdomains
    print("\n### Running Nmap Scans ###")
    for subdomain in subdomains:
        run_nmap_scan(subdomain)

    # Step 3: Run Nikto scans on all subdomains
    print("\n### Running Nikto Scans ###")
    for subdomain in subdomains:
        run_nikto_scan(subdomain)

if __name__ == "__main__":
    main()
