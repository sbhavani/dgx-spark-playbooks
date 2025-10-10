# Set up Tailscale on your Spark

> Use Tailscale to connect to your Spark on your home network no matter where you are

## Table of Contents

- [Overview](#overview)
- [Instructions](#instructions)
  - [Step 1. Verify system requirements](#step-1-verify-system-requirements)
  - [Step 2. Install SSH server (if needed)](#step-2-install-ssh-server-if-needed)
  - [Step 3. Install Tailscale on NVIDIA Spark](#step-3-install-tailscale-on-nvidia-spark)
  - [Step 4. Verify Tailscale installation](#step-4-verify-tailscale-installation)
  - [Step 5. Connect Spark device to Tailscale network](#step-5-connect-spark-device-to-tailscale-network)
  - [Step 6. Install Tailscale on client devices](#step-6-install-tailscale-on-client-devices)
  - [Step 7. Connect client devices to tailnet](#step-7-connect-client-devices-to-tailnet)
  - [Step 8. Verify network connectivity](#step-8-verify-network-connectivity)
  - [Step 9. Configure SSH authentication](#step-9-configure-ssh-authentication)
  - [Step 10. Test SSH connection](#step-10-test-ssh-connection)
  - [Step 11. Validate installation](#step-11-validate-installation)
  - [Step 13. Cleanup and rollback](#step-13-cleanup-and-rollback)
  - [Step 14. Next steps](#step-14-next-steps)
- [Troubleshooting](#troubleshooting)

---

## Overview

## Basic idea

Tailscale creates an encrypted peer-to-peer mesh network that allows secure access
to your NVIDIA Spark device from anywhere without complex firewall configurations
or port forwarding. By installing Tailscale on both your Spark and client devices,
you establish a private "tailnet" where each device gets a stable private IP
address and hostname, enabling seamless SSH access whether you're at home, work,
or a coffee shop.

## What you'll accomplish

You will set up Tailscale on your NVIDIA Spark device and client machines to
create secure remote access. After completion, you'll be able to SSH into your
Spark from anywhere using simple commands like `ssh user@spark-hostname`, with
all traffic automatically encrypted and NAT traversal handled transparently.

## What to know before starting

- Working with terminal/command line interfaces
- Basic SSH concepts and usage
- Installing packages using `apt` on Ubuntu
- Understanding of user accounts and authentication
- Familiarity with systemd service management

## Prerequisites

- NVIDIA Spark device running DGX OS (ARM64/AArch64)
- Client device (Mac, Windows, or Linux) for remote access
- Client device and DGX Spark not on the same network when testing connectivity
- Internet connectivity on both devices
- Valid email account for Tailscale authentication (Google, GitHub, Microsoft)
- SSH server availability check: `systemctl status ssh`
- Package manager working: `sudo apt update`
- User account with sudo privileges on Spark device

## Time & risk

* **Duration**: 15-30 minutes for initial setup, 5 minutes per additional device
* **Risks**:
  * Potential SSH service configuration conflicts
  * Network connectivity issues during initial setup
  * Authentication provider service dependencies
* **Rollback**: Tailscale can be completely removed with `sudo apt remove tailscale` and all network routing automatically reverts to default settings.

## Instructions

### Step 1. Verify system requirements

Check that your NVIDIA Spark device is running a supported Ubuntu version and
has internet connectivity. This step runs on the Spark device to confirm
prerequisites.

```bash
## Check Ubuntu version (should be 20.04 or newer)
lsb_release -a

## Test internet connectivity
ping -c 3 google.com

## Verify you have sudo access
sudo whoami
```

### Step 2. Install SSH server (if needed)

Ensure SSH server is running on your Spark device since Tailscale provides
network connectivity but requires SSH for remote access. This step runs on
the Spark device.

```bash
## Check if SSH is running
systemctl status ssh --no-pager
```

**If SSH is not installed or running:**

```bash
## Install OpenSSH server
sudo apt update
sudo apt install -y openssh-server

## Enable and start SSH service
sudo systemctl enable ssh --now --no-pager

## Verify SSH is running
systemctl status ssh --no-pager
```

### Step 3. Install Tailscale on NVIDIA Spark

Install Tailscale on your ARM64 Spark device using the official Ubuntu
repository. This step adds the Tailscale package repository and installs
the client.

```bash
## Update package list
sudo apt update

## Install required tools for adding external repositories
sudo apt install -y curl gnupg

## Add Tailscale signing key
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/noble.noarmor.gpg | \
  sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg > /dev/null

## Add Tailscale repository
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/noble.tailscale-keyring.list | \
  sudo tee /etc/apt/sources.list.d/tailscale.list

## Update package list with new repository
sudo apt update

## Install Tailscale
sudo apt install -y tailscale
```

### Step 4. Verify Tailscale installation

Confirm Tailscale installed correctly on your Spark device before proceeding
with authentication.

```bash
## Check Tailscale version
tailscale version

## Check Tailscale service status
sudo systemctl status tailscaled --no-pager
```

### Step 5. Connect Spark device to Tailscale network

Authenticate your Spark device with Tailscale using your chosen identity
provider. This creates your private tailnet and assigns a stable IP address.

```bash
## Start Tailscale and begin authentication
sudo tailscale up

## Follow the URL displayed to complete login in browser
## Choose from: Google, GitHub, Microsoft, or other supported providers
```

### Step 6. Install Tailscale on client devices

Install Tailscale on the devices you'll use to connect to your Spark remotely.

Choose the appropriate method for your client operating system.

**On macOS:**
- Option 1: Install from Mac App Store by searching for "Tailscale" and then clicking Get → Install
- Option 2: Download the .pkg installer from the [Tailscale website](https://tailscale.com/download)


**On Windows:**
- Download installer from the [Tailscale website](https://tailscale.com/download)
- Run the .msi file and follow installation prompts
- Launch Tailscale from Start Menu or system tray


**On Linux:**

Use the same instructions as were done for installing on your DGX Spark.

```bash
## Update package list
sudo apt update

## Install required tools for adding external repositories
sudo apt install -y curl gnupg

## Add Tailscale signing key
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/noble.noarmor.gpg | \
  sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg > /dev/null

## Add Tailscale repository
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/noble.tailscale-keyring.list | \
  sudo tee /etc/apt/sources.list.d/tailscale.list

## Update package list with new repository
sudo apt update

## Install Tailscale
sudo apt install -y tailscale
```

### Step 7. Connect client devices to tailnet

Log in to Tailscale on each client device using the same identity provider
account you used for the Spark device.

**On macOS/Windows (GUI):**
- Launch Tailscale app
- Click "Log in" button
- Sign in with same account used on Spark

**On Linux (CLI):**

```bash
## Start Tailscale on client
sudo tailscale up

## Complete authentication in browser using same account
```

### Step 8. Verify network connectivity

Test that devices can communicate through the Tailscale network before
attempting SSH connections.

```bash
## On any device, check tailnet status
tailscale status

## Test ping to Spark device (use hostname or IP from status output)
tailscale ping <SPARK_HOSTNAME>

## Example output should show successful pings
```

### Step 9. Configure SSH authentication

Set up SSH key authentication for secure access to your Spark device. This
step runs on your client device and Spark device.

**Generate SSH key on client (if not already done):**

```bash
## Generate new SSH key pair
ssh-keygen -t ed25519 -f ~/.ssh/tailscale_spark

## Display public key to copy
cat ~/.ssh/tailscale_spark.pub
```

**Add public key to Spark device:**

```bash
## On Spark device, add client's public key
echo "<YOUR_PUBLIC_KEY>" >> ~/.ssh/authorized_keys

## Set correct permissions
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

### Step 10. Test SSH connection

Connect to your Spark device using SSH over the Tailscale network to verify
the complete setup works.

```bash
## Connect using Tailscale hostname (preferred)
ssh -i ~/.ssh/tailscale_spark <USERNAME>@<SPARK_HOSTNAME>

## Or connect using Tailscale IP address
ssh -i ~/.ssh/tailscale_spark <USERNAME>@<TAILSCALE_IP>

## Example:
## ssh -i ~/.ssh/tailscale_spark nvidia@my-spark-device
```

### Step 11. Validate installation

Verify that Tailscale is working correctly and your SSH connection is stable.

```bash
## From client device, check connection status
tailscale status

## Create a test file on the client device
echo "test file for the spark" > test.txt

## Test file transfer over SSH
scp -i ~/.ssh/tailscale_spark test.txt <USERNAME>@<SPARK_HOSTNAME>:~/

## Verify you can run commands remotely
ssh -i ~/.ssh/tailscale_spark <USERNAME>@<SPARK_HOSTNAME> 'nvidia-smi'
```

Expected output:
- Tailscale status displaying both devices as "active"
- Successful file transfers
- Remote command execution working

### Step 13. Cleanup and rollback

Remove Tailscale completely if needed. This will disconnect devices from the
tailnet and remove all network configurations.

> **Warning**: This will permanently remove the device from your Tailscale
> network and require re-authentication to rejoin.

```bash
## Stop Tailscale service
sudo tailscale down

## Remove Tailscale package
sudo apt remove --purge tailscale

## Remove repository and keys (optional)
sudo rm /etc/apt/sources.list.d/tailscale.list
sudo rm /usr/share/keyrings/tailscale-archive-keyring.gpg

## Update package list
sudo apt update
```

To restore: Re-run installation steps 3-5.

### Step 14. Next steps

Your Tailscale setup is complete. You can now:

- Access your Spark device from any network with: `ssh <USERNAME>@<SPARK_HOSTNAME>`
- Transfer files securely: `scp file.txt <USERNAME>@<SPARK_HOSTNAME>:~/`
- Open the DGX Dashboard and start JupyterLab, then connect with:
  `ssh -L 8888:localhost:1102 <USERNAME>@<SPARK_HOSTNAME>`

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `tailscale up` auth fails | Network issues | Check internet, try `curl -I login.tailscale.com` |
| SSH connection refused | SSH not running | Run `sudo systemctl start ssh --no-pager` on Spark |
| SSH auth failure | Wrong SSH keys | Check public key in `~/.ssh/authorized_keys` |
| Cannot ping hostname | DNS issues | Use IP from `tailscale status` instead |
| Devices missing | Different accounts | Use same identity provider for all devices |

> **Note:** DGX Spark uses a Unified Memory Architecture (UMA), which enables dynamic memory sharing between the GPU and CPU. 
> With many applications still updating to take advantage of UMA, you may encounter memory issues even when within 
> the memory capacity of DGX Spark. If that happens, manually flush the buffer cache with:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
