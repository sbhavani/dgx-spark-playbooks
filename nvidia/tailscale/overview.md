# Basic idea

Tailscale creates an encrypted peer-to-peer mesh network that allows secure access
to your NVIDIA Spark device from anywhere without complex firewall configurations
or port forwarding. By installing Tailscale on both your Spark and client devices,
you establish a private "tailnet" where each device gets a stable private IP
address and hostname, enabling seamless SSH access whether you're at home, work,
or a coffee shop.

# What you'll accomplish

You will set up Tailscale on your NVIDIA Spark device and client machines to
create secure remote access. After completion, you'll be able to SSH into your
Spark from anywhere using simple commands like `ssh user@spark-hostname`, with
all traffic automatically encrypted and NAT traversal handled transparently.

# What to know before starting

- Working with terminal/command line interfaces
- Basic SSH concepts and usage
- Installing packages using `apt` on Ubuntu
- Understanding of user accounts and authentication
- Familiarity with systemd service management

# Prerequisites

- NVIDIA Spark device running DGX OS (ARM64/AArch64)
- Client device (Mac, Windows, or Linux) for remote access
- Client device and DGX Spark not on the same network when testing connectivity
- Internet connectivity on both devices
- Valid email account for Tailscale authentication (Google, GitHub, Microsoft)
- SSH server availability check: `systemctl status ssh`
- Package manager working: `sudo apt update`
- User account with sudo privileges on Spark device

# Time & risk

* **Duration**: 15-30 minutes for initial setup, 5 minutes per additional device
* **Risks**:
* Potential SSH service configuration conflicts
* Network connectivity issues during initial setup
* Authentication provider service dependencies
* **Rollback**: Tailscale can be completely removed with `sudo apt remove tailscale` and all network routing automatically reverts to default settings.
