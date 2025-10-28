# Step 1. Install and configure NVIDIA Sync

Follow the [NVIDIA Sync setup guide](/spark/connect-to-your-spark/sync) to:
- Install NVIDIA Sync for your operating system
- Configure which development tools you want to use (VS Code, Cursor, Terminal, etc.)
- Add your DGX Spark device by providing its hostname/IP and credentials

NVIDIA Sync will automatically configure SSH key-based authentication for secure, password-free access.

# Step 2. Launch VS Code through NVIDIA Sync

- Click the NVIDIA Sync icon in your system tray/taskbar
- Ensure your device is connected (click "Connect" if needed)
- Click on "VS Code" to launch it with an automatic SSH connection to your Spark
- Wait for the remote connection to be established (may ask your local machine for a password or to authorize the connection)
- It may prompt you to "trust the authors of the files in this folder" when you first land in the home directory after a successful SSH connection

# Step 3. Validation and follow-ups

- Verify that you can access your Spark's filesystem with VS Code as a text editor
- Open the integrated terminal in VS Code and run test commands like `hostnamectl` and `whoami` to ensure you are remotely accessing your Spark
- Navigate to a specific file path or directory and start editing/writing files
- Install VS Code extensions for your development workflow (Python, Docker, GitLens, etc.)
- Clone repositories from GitHub or other version control systems
- Configure and locally host an LLM code assistant if desired
