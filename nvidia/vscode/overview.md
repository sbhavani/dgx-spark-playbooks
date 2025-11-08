# Basic idea
This walkthrough establishes a local Visual Studio Code development environment directly on DGX Spark devices. By installing VS Code natively on the ARM64-based Spark system, you gain access to a full-featured IDE with extensions, integrated terminal, and Git integration while leveraging the specialized hardware for development and testing.

# What you'll accomplish
You will have Visual Studio Code running natively on your DGX Spark device with access to the system's ARM64 architecture and GPU resources. This setup enables direct code development, debugging, and execution on the target hardware without remote development overhead.

# What to know before starting

• Basic experience working with Visual Studio Code interface and features

• Familiarity with package management on Linux systems

• Understanding of file permissions and authentication on Linux

# Prerequisites

• DGX Spark device with administrative privileges

• Active internet connection for downloading the VS Code installer

• Verify ARM64 architecture:
  ```bash
  uname -m
  # Expected output: aarch64
  ```
• Verify GUI desktop environment available:
  ```bash
  echo $DISPLAY
  # Should return display information like :0 or :10.0
  ```


# Time & risk

* **Duration:** 10-15 minutes
* **Risk level:** Low - installation uses official packages with standard rollback
* **Rollback:** Standard package removal via system package manager
