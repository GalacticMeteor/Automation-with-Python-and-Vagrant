import subprocess

def install_and_start_apache():
    try:
        print("Updating package list...")
        subprocess.check_call(['sudo', 'apt', 'update'])

        print("Installing Apache...")
        subprocess.check_call(['sudo', 'apt', 'install', '-y', 'apache2'])

        print("Enabling Apache to start on boot...")
        subprocess.check_call(['sudo', 'systemctl', 'enable', 'apache2'])

        print("Starting Apache service...")
        subprocess.check_call(['sudo', 'systemctl', 'start', 'apache2'])

        print("Apache is installed and running.")
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")

install_and_start_apache()
