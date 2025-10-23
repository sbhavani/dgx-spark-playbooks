# Basic idea

The DGX Dashboard is a web application that runs locally on DGX Spark devices, providing a graphical interface for system updates, resource monitoring and an integrated JupyterLab environment. Users can access the dashboard locally from the app launcher or remotely through NVIDIA Sync or SSH tunneling. The dashboard is the easiest way to update system packages and firmware when working remotely.

# What you'll accomplish

You will learn how to access and use the DGX Dashboard on your DGX Spark device. By the end of this walkthrough, you will be able to launch JupyterLab instances with pre-configured Python environments, monitor GPU performance, manage system updates and run a sample AI workload using Stable Diffusion. You'll understand multiple access methods including desktop shortcuts, NVIDIA Sync and manual SSH tunneling.

# What to know before starting

- Basic terminal usage for SSH connections and port forwarding
- Understanding of Python environments and Jupyter notebooks

# Prerequisites

- DGX Spark device with Ubuntu Desktop environment
- NVIDIA Sync installed (for remote access method) or SSH client configured

# Ancillary files

- Python code snippet for SDXL found [here on GitHub](${GITLAB_ASSET_BASEURL}/${MODEL}/assets/jupyter-cell.py)


# Time & risk

* **Duration:** 15-30 minutes for complete walkthrough including sample AI workload
* **Risk level:** Low - Web interface operations with minimal system impact
* **Rollback:** Stop JupyterLab instances through dashboard interface; no permanent system changes made during normal usage.
