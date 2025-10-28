# Common issues for running on two Spark

| Issue | Cause | Solution |
|-------|-------|----------|
| mpirun hangs or times out | SSH connectivity issues | 1. Test basic SSH connectivity: `ssh <remote_ip>` should work without password prompts<br>2. Try a simple mpirun test: `mpirun -np 2 -H <IP for Node 1>:1,<IP for Node 2>:1 hostname`<br>3. Verify SSH keys are setup correctly for all nodes |
| Network interface not found | Wrong interface name or down status | Check interface status with `ibdev2netdev` and verify IP configuration |
| NCCL build fails | Missing dependencies such as OpenMPI or incorrect CUDA version | Verify CUDA installation and required libraries are present |
