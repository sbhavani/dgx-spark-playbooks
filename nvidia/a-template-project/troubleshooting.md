<!-- 
TROUBLESHOOTING TEMPLATE: Although optional, this resource can significantly help users resolve common issues.
Replace all placeholder content in {} with your actual troubleshooting information.
Remove these comment blocks when you're done.

PURPOSE: Provide quick solutions to problems users are likely to encounter.
FORMAT: Use the table format for easy scanning. Add detailed notes when needed.
-->

| Symptom | Cause | Fix |
|---------|-------|-----|
| {Specific error message or behavior} | {Root cause of the problem} | {Specific steps to resolve} |

<!-- Add more rows as needed for your specific tool -->



<!-- 
Space reserved for some common known issues that might be relevant to your project. Assess potential consequences before changing or deleting.
-->

> [!NOTE] 
> DGX Spark uses a Unified Memory Architecture (UMA), which enables dynamic memory sharing between the GPU and CPU. 
> With many applications still updating to take advantage of UMA, you may encounter memory issues even when within 
> the memory capacity of DGX Spark. If that happens, manually flush the buffer cache with:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```