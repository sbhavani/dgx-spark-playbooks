| Symptom | Cause | Fix |
|---------|-------|-----|
| `dpkg: dependency problems` during install | Missing dependencies | Run `sudo apt-get install -f` |
| VS Code won't launch with GUI error | No display server/X11 | Verify GUI desktop is running: `echo $DISPLAY` |
| Extensions fail to install | Network connectivity or ARM64 compatibility | Check internet connection, verify extension ARM64 support |
