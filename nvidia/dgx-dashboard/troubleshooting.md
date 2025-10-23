| Symptom | Cause | Fix |
|---------|-------|-----|
| User can't run updates | User not in sudo group | Add user to sudo group: `sudo usermod -aG sudo <USERNAME>`; then run `newgrp docker`|
| JupyterLab won't start | Issue with current virtual environment | Change the working directory in the JupyterLab panel and start a new instance |
| SSH tunnel connection refused | Incorrect IP or port | Verify Spark device IP and ensure SSH service is running |
| GPU not visible in monitoring | Driver issues | Check GPU status with `nvidia-smi` |
