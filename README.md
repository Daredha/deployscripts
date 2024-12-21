# Deploy Scripts

This repository contains deployment scripts and automation tools for various deployment scenarios.

## Current scripts:
- Deploy Valeros with ElasticSearch and Oxigraph (BETA, v0.1.0)

## Contents

- Deployment automation scripts
- Configuration templates
- Utility functions

## Getting Started

### 0. Prerequisites

Before running the deployment scripts, you should have:

* A (virtual) machine with Ubuntu installed
* A generated SSH key pair (see below)

### 1. Generate SSH Key Pair

To generate a SSH key pair, follow these steps:

1. Open a terminal on your Windows machine
2. Run the command `ssh-keygen -t rsa -b 4096`
3. Set and remember a password for your key pair

### 2. Copy SSH Key to Ubuntu

To copy the SSH key to the Ubuntu machine, follow these steps:

0. Open a terminal on your Windows machine
1. Run the command
     `type $env:USERPROFILE\.ssh\id_rsa.pub | ssh your-username@your-vm-ip "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"`
2. Enter `yes` to confirm the connection
3. Enter the password for your key pair

### 3. Connect to Ubuntu via SSH

To connect to the Ubuntu machine via SSH, follow these steps:

0. Open a terminal on your Windows machine
1. Run the command `ssh your-username@your-vm-ip`
2. Enter the password for your key pair

### 4. Install Ansible

To install Ansible on the Ubuntu machine, follow these steps:

0. Connect to the Ubuntu machine via SSH
1. Run the command `sudo apt-get install ansible -y`


### 5. Run Deployment Script

To run the deployment script, follow these steps:
(Assuming version 0.1.0)
1. Download the latest version of the deployment scripts via:
 `wget https://github.com/Daredha/deployscripts/archive/refs/tags/v0.1.0.tar.gz`
2. Unzip the downloaded file: `tar -xzvf v0.1.0.tar.gz`
3. Change into the unzipped directory: `cd deployscripts-0.1.0`
4. Run the command to start a script. For example: `sudo ansible-playbook --connection=local --inventory 127.0.0.1, server_setup.yml`

The deployment script will automatically run the necessary commands to set up the Ubuntu machine for deployment. This can take a few minutes to complete.


## Contributing

Feel free to contribute to this project. Please open an issue or a pull request if you have any suggestions or find any bugs.
