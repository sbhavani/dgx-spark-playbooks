# Basic idea

Configure two DGX Spark systems for high-speed inter-node communication using 200GbE direct
QSFP connections. This setup enables distributed workloads across multiple DGX Spark nodes
by establishing network connectivity and configuring SSH authentication.

# What you'll accomplish

You will physically connect two DGX Spark devices with a QSFP cable, configure network
interfaces for cluster communication, and establish passwordless SSH between nodes to create
a functional distributed computing environment.

# What to know before starting

- Basic understanding of distributed computing concepts
- Working with network interface configuration and netplan
- Experience with SSH key management

# Prerequisites

- Two DGX Spark systems
- One QSFP cable for direct 200GbE connection between two devices
- SSH access available to both systems
- Root or sudo access on both systems: `sudo whoami`
- The same username on both systems

# Ancillary files

All required files for this playbook can be found [here on GitHub](${GITLAB_ASSET_BASEURL}/${MODEL}/)

- [**discover-sparks.sh**](${GITLAB_ASSET_BASEURL}/${MODEL}/assets/discover-sparks) script for automatic node discovery and SSH key distribution

# Time & risk

- **Duration:** 1 hour including validation

- **Risk level:** Medium - involves network reconfiguration

- **Rollback:** Network changes can be reversed by removing netplan configs or IP assignments
