# Possible issues connecting via NVIDIA Sync

| Symptom | Cause | Fix |
|---------|--------|-----|
| Device name doesn't resolve | mDNS blocked on network | Use IP address instead of hostname.local |
| Connection refused/timeout | DGX Spark not booted or SSH not ready | Wait for device boot completion; SSH available after updates finish |
| Authentication failed | SSH key setup incomplete | Re-run device setup in NVIDIA Sync; check credentials |

# Possible issues connecting via manual SSH

| Symptom | Cause | Fix |
|---------|--------|-----|
| Device name doesn't resolve | mDNS blocked on network | Use IP address instead of hostname.local |
| Connection refused/timeout | DGX Spark not booted or SSH not ready | Wait for device boot completion; SSH available after updates finish |
| Port forwarding fails | Service not running or port conflict | Verify remote service is active; try different local port |
