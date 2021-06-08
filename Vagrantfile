# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.hostmanager.enabled = true
  config.hostmanager.manage_host = true
  config.hostmanager.manage_guest = true
  config.vm.box_url = "https://download.fedoraproject.org/pub/fedora/linux/releases/34/Cloud/x86_64/images/Fedora-Cloud-Base-Vagrant-34-1.2.x86_64.vagrant-libvirt.box"
  config.vm.box = "f34-cloud-libvirt"
  config.vm.hostname = "bugzilla2fedmsg.test"
  config.vm.synced_folder ".", "/home/vagrant/bugzilla2fedmsg", type: "sshfs"

  config.vm.provider :libvirt do |libvirt|
    libvirt.cpus = 2
    libvirt.memory = 2048
  end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "devel/ansible/playbook.yml"
    ansible.config_file = "devel/ansible/ansible.cfg"
  end

end
