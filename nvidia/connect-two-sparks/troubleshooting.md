| Symptom | Cause | Fix |
|---------|-------|-----|
| "Network unreachable" errors | Network interfaces not configured | Verify netplan config and `sudo netplan apply` |
| SSH authentication failures | SSH keys not properly distributed | Re-run `./discover-sparks` and enter passwords |
| Node 2 not visible in cluster | Network connectivity issue | Verify QSFP cable connection, check IP configuration |
