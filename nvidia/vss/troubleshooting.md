| Symptom | Cause | Fix |
|---------|--------|-----|
| Container fails to start with "pull access denied" | Missing or incorrect nvcr.io credentials | Re-run `docker login nvcr.io` with valid credentials |
| Network creation fails | Existing network with same name | Run `docker network rm vss-shared-network` then recreate |
| Services fail to communicate | Incorrect environment variables | Verify `IS_SBSA=1 IS_AARCH64=1` are set correctly |
| Web interfaces not accessible | Services still starting or port conflicts | Wait 2-3 minutes, check `docker ps` for container status |

> [!NOTE]
> DGX Spark uses a Unified Memory Architecture (UMA), which enables dynamic memory sharing between the GPU and CPU. 
> With many applications still updating to take advantage of UMA, you may encounter memory issues even when within 
> the memory capacity of DGX Spark. If that happens, manually flush the buffer cache with:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
