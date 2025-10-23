# Basic idea

If you primarily work on another system, such as a laptop, and want to use your DGX Spark as a
remote resource, this playbook shows you how to connect and work over SSH. With SSH, you can
securely open a terminal session or tunnel ports to access web apps and APIs on your DGX Spark
from your local machine. 

There are two approaches: **NVIDIA Sync (recommended)** for streamlined
device management, or **manual SSH** for direct command-line control.

Before you get started, there are some important concepts to understand:

**Secure Shell (SSH)** is a cryptographic protocol for securely connecting to a remote computer
over an untrusted network. It lets you open a terminal on your DGX Spark as if you were sitting
at it, run commands, transfer files, and manage services—all encrypted end-to-end.

**SSH tunneling** (also called port forwarding) securely maps a port on your laptop
(for example, localhost:8888) to a port on the DGX Spark where an app is listening
(such as JupyterLab on port 8888). Your browser connects to localhost, and SSH forwards
the traffic through the encrypted connection to the remote service without exposing
that port on the wider network.

**mDNS (Multicast DNS)** lets devices discover each other by name on a local network without
needing a central DNS server. Your DGX Spark advertises its hostname via mDNS, so you can
connect using a name like `spark-abcd.local` (note the .local suffix), rather than looking
up its IP address.

# What you'll accomplish

You will establish secure SSH access to your DGX Spark device using either NVIDIA Sync or manual
SSH configuration. NVIDIA Sync provides a graphical interface for device management with
integrated app launching, while manual SSH gives you direct command-line control with port
forwarding capabilities. Both approaches enable you to run terminal commands, access web
applications, and manage your DGX Spark remotely from your laptop.


# What to know before starting

- Basic terminal/command line usage
- Understanding of SSH concepts and key-based authentication
- Familiarity with network concepts like hostnames, IP addresses, and port forwarding

# Prerequisites

- DGX Spark device is set up and you have created a local user account
- Your laptop and DGX Spark are on the same network
- You have your DGX Spark username and password
- You have your device's mDNS hostname (printed on quick start guide) or IP address



# Time & risk

- **Time estimate:** 5-10 minutes
- **Risk level:** Low - SSH setup involves credential configuration but no system-level changes to the DGX Spark device
- **Rollback:** SSH key removal can be done by editing `~/.ssh/authorized_keys` on the DGX Spark.
