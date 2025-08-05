#!/usr/bin/env python3

import subprocess
import sys
import os
import re
import shutil
from pathlib import Path

def run_command(cmd, check=True, shell=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(cmd, shell=shell, check=check, 
                              capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {cmd}")
        print(f"[ERROR] Exit code: {e.returncode}")
        print(f"[ERROR] Output: {e.stderr}")
        if check:
            sys.exit(1)
        return None

def get_vm_ip():
    """Get the VM's IP address using the same method as the bash script"""
    try:
        output = run_command("ip route get 8.8.8.8")
        # Parse the output to find the src IP
        for i, word in enumerate(output.split()):
            if word == "src" and i + 1 < len(output.split()):
                return output.split()[i + 1]
        raise ValueError("Could not find src IP in route output")
    except Exception as e:
        print(f"[ERROR] Failed to get VM IP: {e}")
        sys.exit(1)

def install_packages():
    """Install bind9 and DNS tools"""
    print("[+] Installing bind9 and DNS tools...")
    run_command("apt-get update")
    run_command("apt-get install -y bind9 bind9utils dnsutils")

def create_zone_directory():
    """Create DNS zone directory"""
    print("[+] Creating DNS zone directory...")
    Path("/etc/bind/zones").mkdir(parents=True, exist_ok=True)

def create_zone_file(vm_ip):
    """Create the DNS zone file for mypyapp.local"""
    print("[+] Defining zone file for mypyapp.local...")
    
    zone_content = f"""$TTL    604800
@       IN      SOA     ns.mypyapp.local. admin.mypyapp.local. (
                        2         ; Serial
                        604800    ; Refresh
                        86400     ; Retry
                        2419200   ; Expire
                        604800 )  ; Negative Cache TTL
;
@       IN      NS      ns.mypyapp.local.
ns      IN      A       127.0.0.1
www     IN      A       192.168.1.108
mypyapp.local.    IN      A       192.168.1.108
"""
    
    with open("/etc/bind/zones/db.mypyapp.local", "w") as f:
        f.write(zone_content)

def update_named_conf_local():
    """Add zone configuration to named.conf.local"""
    print("[+] Updating named.conf.local with zone config...")
    
    zone_config = '''
zone "mypyapp.local" {
    type master;
    file "/etc/bind/zones/db.mypyapp.local";
    allow-query { any; };
};
'''
    
    with open("/etc/bind/named.conf.local", "a") as f:
        f.write(zone_config)

def configure_bind_options():
    """Configure BIND9 to accept external queries"""
    print("[+] Configuring BIND9 to accept external queries...")
    
    options_file = "/etc/bind/named.conf.options"
    
    # Read the current content
    with open(options_file, "r") as f:
        content = f.read()
    
    # Add listen-on directive if not present
    if "listen-on { any; };" not in content:
        content = re.sub(
            r'listen-on-v6 { any; };',
            r'listen-on-v6 { any; };\n\tlisten-on { any; };',
            content
        )
    
    # Configure forwarders
    forwarders_config = "\tforwarders {\n\t\t8.8.8.8;\n\t\t8.8.4.4;\n\t};"
    
    # Replace the commented forwarders section
    content = re.sub(
        r'//\s*forwarders\s*{.*?//\s*};',
        forwarders_config,
        content,
        flags=re.DOTALL
    )
    
    # Write back the modified content
    with open(options_file, "w") as f:
        f.write(content)

def check_bind_configuration():
    """Check BIND configuration syntax"""
    print("[+] Checking bind configuration syntax...")
    run_command("named-checkconf")
    run_command("named-checkzone mypyapp.local /etc/bind/zones/db.mypyapp.local")

def restart_bind_service():
    """Restart and enable bind9 service"""
    print("[+] Restarting bind9...")
    run_command("systemctl restart named")
    run_command("systemctl enable named")

def is_systemd_resolved_active():
    """Check if systemd-resolved is active"""
    try:
        result = run_command("systemctl is-active systemd-resolved", check=False)
        return result == "active"
    except:
        return False

def configure_dns_resolution():
    """Configure DNS resolution"""
    print("[+] Configuring DNS resolution...")
    
    if is_systemd_resolved_active():
        print("[+] Configuring systemd-resolved to use 127.0.0.1 as DNS...")
        
        resolved_conf = "/etc/systemd/resolved.conf"
        
        # Read current content
        with open(resolved_conf, "r") as f:
            content = f.read()
        
        # Update DNS and FallbackDNS settings
        content = re.sub(r'^#?DNS=.*', 'DNS=127.0.0.1', content, flags=re.MULTILINE)
        content = re.sub(r'^#?FallbackDNS=.*', 'FallbackDNS=8.8.8.8', content, flags=re.MULTILINE)
        
        # Write back the modified content
        with open(resolved_conf, "w") as f:
            f.write(content)
        
        # Create symlink and restart service
        resolv_link = Path("/etc/resolv.conf")
        if resolv_link.exists() or resolv_link.is_symlink():
            resolv_link.unlink()
        resolv_link.symlink_to("/run/systemd/resolve/resolv.conf")
        
        run_command("systemctl restart systemd-resolved")
    
    else:
        print("[+] systemd-resolved not available, configuring /etc/resolv.conf directly...")
        
        # Backup original resolv.conf
        shutil.copy2("/etc/resolv.conf", "/etc/resolv.conf.backup")
        
        # Create new resolv.conf
        resolv_content = """nameserver 127.0.0.1
nameserver 8.8.8.8
nameserver 8.8.4.4
search mypyapp.local
"""
        
        with open("/etc/resolv.conf", "w") as f:
            f.write(resolv_content)

def main():
    """Main function to orchestrate the DNS setup"""
    # Check if running as root
    if os.geteuid() != 0:
        print("[ERROR] This script must be run as root (use sudo)")
        sys.exit(1)
    
    try:
        # Get VM IP address
        vm_ip = get_vm_ip()
        print(f"[+] Detected VM IP address: {vm_ip}")
        
        # Execute setup steps
        install_packages()
        create_zone_directory()
        create_zone_file(vm_ip)
        update_named_conf_local()
        configure_bind_options()
        check_bind_configuration()
        restart_bind_service()
        configure_dns_resolution()
        
        print("\n[SUCCESS] DNS server setup completed successfully!")
        print(f"[INFO] You can now resolve mypyapp.local to {vm_ip}")
        print("[INFO] Test with: nslookup mypyapp.local")
        
    except KeyboardInterrupt:
        print("\n[ERROR] Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()