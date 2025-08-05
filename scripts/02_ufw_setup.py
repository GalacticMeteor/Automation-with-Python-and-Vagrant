import subprocess
print("[INFO] Installing and configuring UFW firewall")

def install_and_start_ufw():
    try:
        print("Updating package list...")
        subprocess.check_call(['sudo', 'apt', 'update'])

        print("Installing ufw...")
        subprocess.check_call(['sudo', 'apt', 'install', '-y', 'ufw'])

        print("Enabling openssh ...")
        subprocess.check_call(['sudo', 'ufw', 'allow', 'OpenSSH'])

        print("Enabling port 80/tcp ...")
        subprocess.check_call(['sudo', 'ufw', 'allow', '80/tcp'])

        print("Enabling port 443/tcp ...")
        subprocess.check_call(['sudo', 'ufw', 'allow', '443/tcp'])

        print("Enabling ufw to start on boot...")
        subprocess.check_call(['sudo', 'ufw', '--force', 'enable'])

        print("ufw is installed and running.")
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")

install_and_start_ufw()
