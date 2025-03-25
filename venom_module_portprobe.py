import argparse
import subprocess
import socket
import paramiko  # For SSH testing (install with `pip install paramiko`)

# Function to get subdomains using Subfinder
def get_subdomains(url):
    try:
        result = subprocess.run(['subfinder', '-d', url], capture_output=True, text=True)
        subdomains = result.stdout.splitlines()
        return [s for s in subdomains if s]  # Filter out empty lines
    except FileNotFoundError:
        print("Error: Subfinder not found. Please install it (e.g., 'go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest').")
        return []

# Run Nmap scan with real-time output and return open ports
def run_nmap_scan(subdomain):
    print(f"\n### Starting Nmap Scan for {subdomain} ###")
    open_ports = []
    process = subprocess.Popen(
        ['nmap', '-sV', '-p', '22,23,80,443', subdomain],  # Scan SSH, Telnet, HTTP, HTTPS
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    # Print output in real-time and parse open ports
    for line in process.stdout:
        print(line, end='')
        if "open" in line and "tcp" in line:
            port = int(line.split('/')[0])
            open_ports.append(port)
    process.wait()
    return open_ports

# Test weak/no credentials on open ports
def test_credentials(subdomain, port):
    weak_creds = [
        ("admin", "admin"),
        ("root", "1234"),
        ("user", "password"),
        ("", "")  # No credentials
    ]
    
    try:
        ip = socket.gethostbyname(subdomain)
    except socket.gaierror:
        print(f"[-] Could not resolve {subdomain} to an IP")
        return

    if port == 22:  # SSH
        print(f"\n[*] Testing SSH on {subdomain}:{port}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        for username, password in weak_creds:
            try:
                ssh.connect(ip, port=port, username=username, password=password, timeout=3)
                print(f"[!] Weak/No credentials found on SSH: {username}:{password}")
                ssh.close()
                return
            except paramiko.AuthenticationException:
                pass  # Authentication failed, try next
            except Exception as e:
                break  # Likely not an SSH service or connection issue
        print(f"[-] No weak credentials detected on SSH port {port}")
        ssh.close()
    
    elif port == 23:  # Telnet with socket
        print(f"\n[*] Testing Telnet on {subdomain}:{port}...")
        for username, password in weak_creds:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((ip, port))
                if username:
                    s.send(username.encode('ascii') + b"\n")
                if password:
                    s.send(password.encode('ascii') + b"\n")
                response = s.recv(1024).decode('ascii', errors='ignore')
                if ">" in response or "#" in response or "login" not in response.lower():
                    print(f"[!] Possible weak/no credentials on Telnet: {username}:{password}")
                    s.close()
                    return
                s.close()
            except Exception as e:
                pass
        print(f"[-] No weak credentials detected on Telnet port {port}")
    
    else:
        print(f"[-] No credential test implemented for port {port}")

# Main function
def main():
    parser = argparse.ArgumentParser(description="Subdomain Scanner with Nmap and Credential Check")
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

    # Step 2: Run Nmap scans on all subdomains and collect open ports
    print("\n### Running Nmap Scans ###")
    subdomain_ports = {}
    for subdomain in subdomains:
        open_ports = run_nmap_scan(subdomain)
        if open_ports:
            subdomain_ports[subdomain] = open_ports

    # Step 3: Test credentials on open ports
    print("\n### Testing Credentials on Open Ports ###")
    for subdomain, ports in subdomain_ports.items():
        for port in ports:
            test_credentials(subdomain, port)

if __name__ == "__main__":
    main()
