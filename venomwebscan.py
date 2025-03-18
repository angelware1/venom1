import argparse
import subprocess
import os
import requests
from sslyze import *


def get_subdomains(url):
    try:
        result = subprocess.run(['subfinder', '-d', url], capture_output=True, text=True)
        return result.stdout.splitlines()
    except FileNotFoundError:
        print("Error: Subfinder not found. Please install it.")
        return []


def is_port_open(nmap_output, port):
    return any(f"{port}/tcp" in line and "open" in line for line in nmap_output.splitlines())


def get_web_protocol(nmap_output):
    if is_port_open(nmap_output, 443):
        return "https"
    elif is_port_open(nmap_output, 80):
        return "http"
    return None


def run_nmap_scan(subdomains):
    nmap_results = {}
    for subdomain in subdomains:
        print(f"[+] Running Nmap scan on {subdomain}")
        try:
            result = subprocess.run([
                'nmap', '-T4', '-p', '22,80,443,8080,8443,5000,8000,8888,8889',
                '--script', 'http-enum,ssl-cert,http-headers,http-title,http-methods,http-security-headers,http-cors,ssl-enum-ciphers,vulners,http-default-accounts',
                '--min-parallelism', '10', '--max-parallelism', '100', subdomain
            ], capture_output=True, text=True, timeout=300)
            nmap_results[subdomain] = result.stdout
        except subprocess.TimeoutExpired:
            nmap_results[subdomain] = "Nmap scan timed out"
        except FileNotFoundError:
            nmap_results[subdomain] = "Nmap not found"
    return nmap_results


def extract_vulnerabilities(nmap_output):
    vulnerabilities = []
    lines = nmap_output.splitlines()
    in_vulners = False
    for line in lines:
        if '| vulners:' in line:
            in_vulners = True
        elif in_vulners and 'CVE-' in line and line.strip().startswith('|'):
            parts = line.split()
            if len(parts) >= 4:
                vulnerabilities.append((parts[1], parts[2], parts[3]))
        elif in_vulners and not line.strip().startswith('|'):
            in_vulners = False
        elif 'CVE-' in line and line.strip().startswith('|'):
            
            parts = line.split(':')
            if len(parts) > 1:
                vuln_desc = parts[1].strip()
                cve = next((part for part in vuln_desc.split() if 'CVE-' in part), None)
                if cve:
                    vulnerabilities.append((cve, "Unknown", vuln_desc))
    return vulnerabilities


def extract_default_credentials(nmap_output):
    credentials = []
    for line in nmap_output.splitlines():
        if "http-default-accounts" in line and "LOGIN" in line:
            cred_part = line.split("LOGIN")[1].strip()
            credentials.append(cred_part)
    return credentials


def check_config_files(subdomain, protocol):
    config_files = [
        '.env', 'config.php', 'web.config', 'settings.py', 'config.json',
        'config.ini', 'config.yaml', 'config.yml', 'application.properties',
        'database.yml', 'wp-config.php', 'config.xml', 'configuration.php',
        'localsettings.php', 'config.inc.php', 'secrets.yaml', 'app.conf',
        'server.cfg', 'site.conf', 'global.asa', 'boot.ini', 'settings.ini',
        'php.ini', 'nginx.conf', 'httpd.conf', 'apache2.conf', 'db.conf'
    ]
    exposed_files = []
    for file in config_files:
        url = f"{protocol}://{subdomain}/{file}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                exposed_files.append(file)
        except requests.RequestException:
            pass
    return exposed_files


def check_sensitive_files(subdomain, protocol):
    sensitive_files = [
        '.git/config', '.svn/entries', '.DS_Store', 'error.log', 'access.log',
        'backup.zip', 'dump.sql', 'database.sql', 'index.php.bak', 'config.php.bak',
        'passwords.txt', 'creds.json', 'private.key', 'id_rsa', 'users.csv',
        'admin.html', 'login.php', 'backup.tar.gz', 'site.backup', 'keys.txt',
        'api.key', 'secret.key', 'db_password.txt', 'config/secrets.yml',
        'data/export.csv', 'internal/docs/confidential.pdf', 'auth.json',
        'credentials.xml', 'pass.txt', 'key.pem'
    ]
    exposed_files = []
    for file in sensitive_files:
        url = f"{protocol}://{subdomain}/{file}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                exposed_files.append(file)
        except requests.RequestException:
            pass
    return exposed_files


def check_dangerous_directories(subdomain, protocol):
    dangerous_paths = [
        'wp-admin', 'wp-login.php', 'wordpress', 'wp-content', 'wp-includes',  # WordPress
        'login', 'signin', 'admin/login.php', 'user/login', 'auth',  # Login pages
        'owa', 'mail', 'webmail', 'outlook', 'exchange',  # Outlook/Email
        'phpmyadmin', 'adminer', 'pma',  # PHP database management
        'apache', 'server-status', 'server-info',  # Apache
        'webcam', 'camera', 'live', 'stream',  # Webcam
        'admin', 'administrator', 'manage', 'manager', 'controlpanel', 'cpanel',  # Admin pages
        'js', 'javascript', 'scripts',  # JavaScript directories
        'tomcat', 'manager/html', 'host-manager',  # Tomcat manager
        'phpinfo.php', 'info.php', 'test.php',  # PHP info/test files
        'cgi-bin', 'bin', 'scripts/cgi',  # CGI scripts
        'uploads', 'files', 'media', 'downloads',  # File upload dirs
        'backup', 'backups', 'archive', 'old',  # Backup dirs
        'dashboard', 'panel', 'control',  # General dashboards
        'api', 'rest', 'graphql',  # API endpoints
        'debug', 'test', 'testing', 'dev', 'staging',  # Dev environments
        'images', 'img', 'pics', 'gif',  # Media (specifically GIFs)
        'config', 'settings', 'conf',  # Additional config dirs
        'db', 'database', 'sql',  # Database dirs
        'logs', 'log', 'audit',  # Log dirs
        'vendor', 'lib', 'libraries',  # Dependency dirs
        'install', 'setup', 'installer',  # Installation dirs
        'portal', 'account', 'profile',  # User portals
        'remote', 'rdp', 'vnc',  # Remote access
        'stats', 'statistics', 'analytics'  # Stats dirs
    ]
    exposed_paths = []
    for path in dangerous_paths:
        url = f"{protocol}://{subdomain}/{path}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                exposed_paths.append(path)
        except requests.RequestException:
            pass
    return exposed_paths


def check_security_headers(subdomain, protocol):
    url = f"{protocol}://{subdomain}"
    try:
        response = requests.get(url, timeout=5)
        headers = response.headers
        missing = [h for h in ['Content-Security-Policy', 'Strict-Transport-Security', 'X-Frame-Options', 'X-Content-Type-Options', 'Referrer-Policy'] if h not in headers]
        return missing
    except requests.RequestException:
        return None


def check_insecure_cookies(subdomain, protocol):
    url = f"{protocol}://{subdomain}"
    try:
        response = requests.get(url, timeout=5)
        insecure = []
        for cookie in response.cookies:
            issues = []
            if protocol == "https" and not cookie.secure:
                issues.append("missing Secure flag")
            if not cookie.has_nonstandard_attr('HttpOnly'):
                issues.append("missing HttpOnly flag")
            if issues:
                insecure.append(f"{cookie.name}: {' and '.join(issues)}")
        return insecure
    except requests.RequestException:
        return None


def run_sslyze_scan(subdomain):
    try:
        server = ServerNetworkLocation(hostname=subdomain, port=443)
        scanner = Scanner()
        scanner.queue_scan(ServerScanRequest(server_location=server))
        for result in scanner.get_results():
            ciphers = result.scan_attempts[0].result.accepted_cipher_suites
            weak_ciphers = [c.name for c in ciphers if "RC4" in c.name or "DES" in c.name]
            return weak_ciphers, None
        return [], None
    except Exception as e:
        return [], f"SSL/TLS analysis failed: {str(e)}"


def run_ssh_audit(subdomain):
    try:
        result = subprocess.run(['ssh-audit', subdomain], capture_output=True, text=True)
        return result.stdout
    except FileNotFoundError:
        return "ssh-audit not found"


def check_default_page(nmap_output):
    default_titles = ["Apache2 Ubuntu Default Page", "Welcome to nginx!", "IIS Windows Server"]
    for port in [80, 443]:
        title = get_http_title(nmap_output, port)
        if title and any(d in title for d in default_titles):
            return True, title
    return False, None

def get_http_title(nmap_output, port):
    for line in nmap_output.splitlines():
        if f"{port}/tcp" in line and "http-title:" in line:
            return line.split("http-title:")[1].strip()
    return None


def check_http_methods(nmap_output):
    dangerous = ["PUT", "DELETE", "TRACE"]
    for port in [80, 443]:
        methods = get_allowed_methods(nmap_output, port)
        if methods:
            risky = [m for m in methods if m in dangerous]
            if risky:
                return True, risky
    return False, []

def get_allowed_methods(nmap_output, port):
    for line in nmap_output.splitlines():
        if f"{port}/tcp" in line and "http-methods:" in line:
            return line.split("http-methods:")[1].strip().split()
    return []


def check_cors_policy(subdomain, protocol):
    url = f"{protocol}://{subdomain}"
    try:
        response = requests.get(url, headers={'Origin': 'http://evil.com'}, timeout=5)
        acao = response.headers.get('Access-Control-Allow-Origin')
        return "Permissive CORS policy" if acao in ['*', 'http://evil.com'] else "Strict CORS policy"
    except requests.RequestException:
        return None


def run_subjack(subdomains):
    with open('subdomains.txt', 'w') as f:
        f.write('\n'.join(subdomains))
    try:
        result = subprocess.run(['subjack', '-w', 'subdomains.txt', '-t', '10', '-o', 'subjack_results.txt'], capture_output=True, text=True)
        return result.stdout
    except FileNotFoundError:
        return "subjack not found"


def get_recommendations(results, subdomain):
    recs = set()
    if results['vulns'][subdomain]:
        recs.add("Update software to patch identified vulnerabilities.")
    if results['creds'][subdomain]:
        recs.add("Change default credentials immediately.")
    if results['config_files'][subdomain]:
        recs.add(f"Secure or remove exposed config files: {', '.join(results['config_files'][subdomain])}.")
    if results['sensitive_files'][subdomain]:
        recs.add(f"Secure or remove exposed sensitive files: {', '.join(results['sensitive_files'][subdomain])}.")
    if results['dangerous_dirs'][subdomain]:
        recs.add(f"Investigate and secure exposed dangerous directories: {', '.join(results['dangerous_dirs'][subdomain])}.")
    if results['headers'][subdomain]:
        recs.add("Add missing security headers.")
    if results['cookies'][subdomain]:
        recs.add("Set Secure and HttpOnly flags on cookies.")
    if results['sslyze'][subdomain][0]:
        recs.add("Disable weak SSL/TLS ciphers.")
    if results['cors'][subdomain] == "Permissive CORS policy":
        recs.add("Restrict CORS policy to trusted origins only.")
    if subdomain in results['default_page']:
        recs.add("Replace default web page with a custom page.")
    if subdomain in results['methods']:
        recs.add(f"Disable dangerous HTTP methods: {', '.join(results['methods'][subdomain])}.")
    if subdomain in results['ssh'] and "not found" not in results['ssh'][subdomain]:
        recs.add("Review and address SSH audit findings.")
    return recs


def main():
    parser = argparse.ArgumentParser(description="Enhanced Web Vulnerability Scanner")
    parser.add_argument('-u', '--url', type=str, required=True, help="Target URL (e.g., example.com)")
    args = parser.parse_args()

    print(f"[+] Discovering subdomains for {args.url}")
    subdomains = get_subdomains(args.url)
    if not subdomains:
        print("No subdomains found or Subfinder failed.")
        return

    print("[+] Subdomains found:")
    for subdomain in subdomains:
        print(f"- {subdomain}")

    results = {
        'config_files': {subdomain: [] for subdomain in subdomains},
        'sensitive_files': {subdomain: [] for subdomain in subdomains},
        'dangerous_dirs': {subdomain: [] for subdomain in subdomains},
        'headers': {subdomain: [] for subdomain in subdomains},
        'cookies': {subdomain: [] for subdomain in subdomains},
        'cors': {subdomain: None for subdomain in subdomains},
        'vulns': {subdomain: [] for subdomain in subdomains},
        'creds': {subdomain: [] for subdomain in subdomains},
        'sslyze': {},
        'ssh': {},
        'default_page': {},
        'methods': {},
    }

    nmap_results = run_nmap_scan(subdomains)

    for subdomain in subdomains:
        nmap_output = nmap_results[subdomain]
        if nmap_output in ["Nmap scan timed out", "Nmap not found"]:
            continue
        protocol = get_web_protocol(nmap_output)
        if protocol:
            results['config_files'][subdomain] = check_config_files(subdomain, protocol)
            results['sensitive_files'][subdomain] = check_sensitive_files(subdomain, protocol)
            results['dangerous_dirs'][subdomain] = check_dangerous_directories(subdomain, protocol)
            results['headers'][subdomain] = check_security_headers(subdomain, protocol) or []
            results['cookies'][subdomain] = check_insecure_cookies(subdomain, protocol) or []
            results['cors'][subdomain] = check_cors_policy(subdomain, protocol)
            if protocol == "https":
                results['sslyze'][subdomain] = run_sslyze_scan(subdomain)
        if is_port_open(nmap_output, 22):
            results['ssh'][subdomain] = run_ssh_audit(subdomain)
        default_found, title = check_default_page(nmap_output)
        if default_found:
            results['default_page'][subdomain] = title
        risky_methods, methods = check_http_methods(nmap_output)
        if risky_methods:
            results['methods'][subdomain] = methods
        results['vulns'][subdomain] = extract_vulnerabilities(nmap_output)
        results['creds'][subdomain] = extract_default_credentials(nmap_output)

        print(f"\n### Results for {subdomain} ###")
        print("\n**Nmap Output:**\n", nmap_output)

    subjack_result = run_subjack(subdomains)

    all_vulns = []
    all_creds = []
    all_config_files = []
    all_sensitive_files = []
    all_dangerous_dirs = []
    all_headers = []
    all_cookies = []
    all_sslyze = []
    all_cors = []
    all_ssh = []
    all_default_pages = []
    all_methods = []
    all_recommendations = set()

    for subdomain in subdomains:
        nmap_output = nmap_results[subdomain]
        if nmap_output in ["Nmap scan timed out", "Nmap not found"]:
            continue
        if results['vulns'][subdomain]:
            for cve, sev, url in results['vulns'][subdomain]:
                all_vulns.append(f"{subdomain}: {cve} (Severity: {sev}) - {url}")
        if results['creds'][subdomain]:
            for cred in results['creds'][subdomain]:
                all_creds.append(f"{subdomain}: {cred}")
        if results['config_files'][subdomain]:
            for file in results['config_files'][subdomain]:
                all_config_files.append(f"{subdomain}: {file}")
        if results['sensitive_files'][subdomain]:
            for file in results['sensitive_files'][subdomain]:
                all_sensitive_files.append(f"{subdomain}: {file}")
        if results['dangerous_dirs'][subdomain]:
            for dir in results['dangerous_dirs'][subdomain]:
                all_dangerous_dirs.append(f"{subdomain}: {dir}")
        if results['headers'][subdomain]:
            for header in results['headers'][subdomain]:
                all_headers.append(f"{subdomain}: {header}")
        if results['cookies'][subdomain]:
            for cookie in results['cookies'][subdomain]:
                all_cookies.append(f"{subdomain}: {cookie}")
        if subdomain in results['sslyze']:
            weak_ciphers, error = results['sslyze'][subdomain]
            if error:
                all_sslyze.append(f"{subdomain}: {error}")
            elif weak_ciphers:
                all_sslyze.append(f"{subdomain}: Weak ciphers: {' '.join(weak_ciphers)}")
        if results['cors'][subdomain]:
            all_cors.append(f"{subdomain}: {results['cors'][subdomain]}")
        if subdomain in results['ssh']:
            all_ssh.append(f"{subdomain}: SSH audit performed")
        if subdomain in results['default_page']:
            all_default_pages.append(f"{subdomain}: {results['default_page'][subdomain]}")
        if subdomain in results['methods']:
            all_methods.append(f"{subdomain}: {', '.join(results['methods'][subdomain])}")
        all_recommendations.update(get_recommendations(results, subdomain))

    print("\n### Subdomain Takeover Results ###\n", subjack_result)

    print("\n### Summary of Findings Across All Subdomains ###")
    if all_vulns:
        print("\n**Vulnerabilities:**")
        for vuln in all_vulns:
            print(f"- {vuln}")
    if all_creds:
        print("\n**Default Credentials Found:**")
        for cred in all_creds:
            print(f"- {cred}")
    if all_config_files:
        print("\n**Exposed Config Files:**")
        for file in all_config_files:
            print(f"- {file}")
    if all_sensitive_files:
        print("\n**Exposed Sensitive Files:**")
        for file in all_sensitive_files:
            print(f"- {file}")
    if all_dangerous_dirs:
        print("\n**Exposed Dangerous Directories/Files:**")
        for dir in all_dangerous_dirs:
            print(f"- {dir}")
    if all_headers:
        print("\n**Missing Headers:**")
        for header in all_headers:
            print(f"- {header}")
    if all_cookies:
        print("\n**Insecure Cookies:**")
        for cookie in all_cookies:
            print(f"- {cookie}")
    if all_sslyze:
        print("\n**SSL/TLS Issues:**")
        for issue in all_sslyze:
            print(f"- {issue}")
    if all_cors:
        print("\n**CORS Policies:**")
        for cors in all_cors:
            print(f"- {cors}")
    if all_ssh:
        print("\n**SSH Audits:**")
        for ssh in all_ssh:
            print(f"- {ssh}")
    if all_default_pages:
        print("\n**Default Pages:**")
        for page in all_default_pages:
            print(f"- {page}")
    if all_methods:
        print("\n**Dangerous HTTP Methods:**")
        for method in all_methods:
            print(f"- {method}")
    if all_recommendations:
        print("\n**Recommendations:**")
        for rec in sorted(all_recommendations):
            print(f"- {rec}")

if __name__ == "__main__":
    main()
