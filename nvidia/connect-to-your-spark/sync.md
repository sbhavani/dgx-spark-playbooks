# Step 1. Install NVIDIA Sync

NVIDIA Sync is a desktop app that connects your computer to your DGX Spark over the local network. 
It gives you a single interface to manage SSH access and launch development tools on your DGX Spark. 

Download and install NVIDIA Sync on your computer to get started.

::spark-download

**For macOS**

- After download, open `nvidia-sync.dmg`
- Drag and drop the app into your Applications folder
- Open `NVIDIA Sync` from the Applications folder

**For Windows**

- After download, run the installer .exe
- NVIDIA Sync will automatically start after installation completes


**For Debian/Ubuntu**

* Configure the package repository:

```
curl -fsSL  https://workbench.download.nvidia.com/stable/linux/gpgkey  |  sudo tee -a /etc/apt/trusted.gpg.d/ai-workbench-desktop-key.asc
echo "deb https://workbench.download.nvidia.com/stable/linux/debian default proprietary" | sudo tee -a /etc/apt/sources.list
```
* Update package lists:

```
sudo apt update
```
* Install NVIDIA Sync:

```
sudo apt install nvidia-sync
```

# Step 2. Configure Apps

Apps are desktop programs installed on your laptop that NVIDIA Sync can configure and launch with an automatic connection to your Spark.

You can change your app selections anytime in the Settings window. Apps that are marked "unavailable" must be installed before you can use them.

**Default apps:**
- **DGX Dashboard**: Web application pre-installed on DGX Spark for system management and integrated JupyterLab access
- **Terminal**: Your system's built-in terminal with automatic SSH connection

**Optional apps (require separate installation):**
- **VS Code**: Download from https://code.visualstudio.com/download 
- **Cursor**: Download from https://cursor.com/downloads 
- **NVIDIA AI Workbench**: Download from https://www.nvidia.com/workbench

# Step 3. Add your DGX Spark device

> [!NOTE]
> You must know either your hostname or IP address to connect.
>
> - The default hostname can be found on the Quick Start Guide included in the box. For example, `spark-abcd.local`
> - If you have a display connected to your device, you can find the hostname on the Settings page of the [DGX Dashboard](http://localhost:11000).
> - If `.local` (mDNS) hostnames don't work on your network you must use an IP address. This can be found in Ubuntu's network settings or by logging into the admin console of your router.

Finally, connect your DGX Spark by filling out the form:

- **Name**: A descriptive name (e.g., "My DGX Spark")
- **Hostname or IP**: The mDNS hostname (e.g. `spark-abcd.local`) or IP address of your Spark
- **Username**: Your DGX Spark user account name
- **Password**: Your DGX Spark user account password

> [!NOTE]
> Your password is used only during this initial setup to configure SSH key-based authentication. It is not stored or transmitted after setup completion. NVIDIA Sync will SSH into your device and 
> configure its locally provisioned SSH key pair.

Click the "Add" button and NVIDIA Sync will automatically:

1. Generate an SSH key pair on your laptop
2. Connect to your DGX Spark using your provided username and password
3. Add the public key to `~/.ssh/authorized_keys` on your device
4. Create an SSH alias locally for future connections
5. Discard your username and password information

> [!IMPORTANT]
> After completing system setup for the first time, your device may take several minutes to update and become available on the network. If NVIDIA Sync fails to connect, please wait 3-4 minutes and try again.

# Step 4. Access your DGX Spark

Once connected, NVIDIA Sync appears as a system tray/taskbar application. Click the NVIDIA Sync
icon to open the device management interface.

- **SSH connection**: Clicking on the large "Connect" and "Disconnect" buttons controls the overall SSH connection to your device.
- **Set working directory** (optional): Choose a default directory that Apps will open in
when launched through NVIDIA Sync. This defaults to your home directory on the remote device.
- **Launch applications**: Click on any configured app to open it with automatic SSH
connection to your DGX Spark.
- **Customize ports** (optional): "Custom Ports" are configured on the Settings screen to provide access to custom web apps or APIs running on your device.

# Step 5. Validate SSH setup

NVIDIA Sync creates an SSH alias for your device for easy access manually or from other SSH enabled apps.

Verify your local SSH configuration is correct by using the SSH alias. You should not be prompted for your 
password when using the alias:

```bash
# Configured if you use mDNS hostname
ssh <SPARK_HOSTNAME>.local
```

or

```bash
# Configured if you use IP address
ssh <IP>
```

On the DGX Spark, verify you're connected:

```bash
hostname
whoami
```

Exit the SSH session:

```bash
exit
```

# Step 6. Next steps

Test your setup by launching a development tool:
- Click the NVIDIA Sync system tray icon.
- Select "Terminal" to open a terminal session on your DGX Spark.
- Select "DGX Dashboard" to use JupyterLab and manage updates.
- Try [a custom port example with Open WebUI](/spark/open-webui/sync).
