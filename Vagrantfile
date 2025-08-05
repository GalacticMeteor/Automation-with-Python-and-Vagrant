Vagrant.configure("2") do |config|
    config.vm.define "VM-F1-PYTHON" do |vm|
      vm.vm.box = "debian/bookworm64"
  
      # Fixed public IP - replace with a valid one from your network
      vm.vm.network "public_network", ip: "192.168.1.108", bridge: "Intel(R) Wi-Fi 6 AX201"  # Change the adapter name
  
      # Disk size (requires plugin)
      vm.disksize.size = '30GB'
  
      # VirtualBox config
      vm.vm.provider "virtualbox" do |vb|
        vb.name = "VM-F1-python"
        vb.memory = 2048  # 2 GB
        vb.cpus = 1       # 1 CPU
      end
  
      vm.vm.synced_folder "./scripts", "/home/vagrant/scripts"
      vm.vm.provision "shell", inline: <<-SHELL
        sudo apt-get update
        sudo apt-get install -y python3

        cd /home/vagrant/scripts
        python3 01_dns_setup.py
        python3 02_ufw_setup.py
        python3 03_apache_setup.py
        python3 04_ssh_setup.py
      SHELL
    end
  end