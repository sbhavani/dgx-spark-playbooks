| Symptom | Cause | Fix |
|---------|-------|-----|
| `tailscale up` auth fails | Network issues | Check internet, try `curl -I login.tailscale.com` |
| SSH connection refused | SSH not running | Run `sudo systemctl start ssh --no-pager` on Spark |
| SSH auth failure | Wrong SSH keys | Check public key in `~/.ssh/authorized_keys` |
| Cannot ping hostname | DNS issues | Use IP from `tailscale status` instead |
| Devices missing | Different accounts | Use same identity provider for all devices |
