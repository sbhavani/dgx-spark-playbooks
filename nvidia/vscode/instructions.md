# Step 1. Verify system requirements

Before installing VS Code, confirm your DGX Spark system meets the requirements and has GUI support.

```bash
# Verify ARM64 architecture
uname -m

# Check available disk space (VS Code requires ~200MB)
df -h /

# Verify desktop environment is running
ps aux | grep -E "(gnome|kde|xfce)"
```

# Step 2. Download VS Code ARM64 installer

Navigate to the VS Code [download](https://code.visualstudio.com/download) page and download the appropriate ARM64 `.deb` package for your system. 

Alternatively, you can download the installer with this command:

```bash
wget https://code.visualstudio.com/sha/download?build=stable\&os=linux-deb-arm64 -O vscode-arm64.deb
```

# Step 3. Install VS Code package

Install the downloaded package using the system package manager. 

You can click on the installer file directly or use the command line. 

```bash
# Install the downloaded .deb package
sudo dpkg -i vscode-arm64.deb

# Fix any dependency issues if they occur
sudo apt-get install -f
```

# Step 4. Verify installation

Confirm the VS Code app is installed successfully and can launch. 

You can open the app directly from the list of applications or use the command line. 

```bash
# Check if VS Code is installed
which code

# Verify version
code --version

# Test launch (will open VS Code GUI)
code &
```

VS Code should launch and display the welcome screen.

# Step 5. Configure for Spark development

Set up VS Code for development on the DGX Spark platform.

```bash
# Launch VS Code if not already running
code

# Or create a new project directory and open it
mkdir ~/spark-dev-workspace
cd ~/spark-dev-workspace
code .
```

From within VS Code:

* Open **File** > **Preferences** > **Settings**
* Search for "terminal integrated shell" to configure default terminal
* Install recommended extensions via **Extensions** tab (left sidebar)

# Step 6. Validate setup and test functionality

Test core VS Code functionality to ensure proper operation on ARM64.

Create a test file:
```bash
# Create test directory and file
mkdir ~/vscode-test
cd ~/vscode-test
echo 'print("Hello from DGX Spark!")' > test.py
code test.py
```

Within VS Code:
* Verify syntax highlighting works
* Open integrated terminal (**Terminal** > **New Terminal**)
* Run the test script: `python3 test.py`
* Test Git integration by running `git status` in the terminal

# Step 8. Uninstalling VS Code

> [!WARNING]
> Uninstalling VS Code will remove all user settings and extensions.

To remove VS Code if needed:
```bash
# Remove VS Code package
sudo apt-get remove code

# Remove configuration files (optional)
rm -rf ~/.config/Code
rm -rf ~/.vscode
```
