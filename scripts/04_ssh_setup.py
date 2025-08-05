import subprocess

def install_and_configure_ssh():
    try:
        print("[INFO] Installing and configuring SSH server")
        print("Update package lists")
        subprocess.check_call(['sudo', 'apt-get', 'update'])
        print("Install openssh-server")
        subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'openssh-server'])
        print("Enable SSH to start on boot")
        subprocess.check_call(['sudo', 'systemctl', 'enable', 'ssh'])
        print("Start SSH service")
        subprocess.check_call(['sudo', 'systemctl', 'start', 'ssh'])
        print("[INFO] SSH server installed, enabled, and started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {e}")

install_and_configure_ssh()
