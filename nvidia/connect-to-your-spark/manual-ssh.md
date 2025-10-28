# Step 1. Verify SSH client availability

Confirm that you have an SSH client installed on your system. Most modern operating systems
include SSH by default. Run the following in your terminal:

```bash
# Check SSH client version
ssh -V
```

Expected output should show OpenSSH version information. 

# Step 2. Gather connection information

Collect the required connection details for your DGX Spark:

- **Username**: Your DGX Spark user account name
- **Password**: Your DGX Spark account password
- **Hostname**: Your device's mDNS hostname (from the Quick Start Guide, e.g., `spark-abcd.local`)
- **IP Address**: An alternative only needed if mDNS doesn't work on your network as described below

In some network configurations, like complex corporate environments, mDNS won't work as expected 
and you'll have to use your device's IP address directly to connect. You'll know you are in this situation when
you try to SSH and the command hangs indefinitely or you get an error like:

```
ssh: Could not resolve hostname spark-abcd.local: Name or service not known
```

**Testing mDNS Resolution**

To test if mDNS is working, use the `ping` utility:

```bash
ping spark-abcd.local
```

If mDNS is working and you can SSH using the hostname, you should see something like this:

```
$ ping -c 3 spark-abcd.local
PING spark-abcd.local (10.9.1.9): 56 data bytes
64 bytes from 10.9.1.9: icmp_seq=0 ttl=64 time=6.902 ms
64 bytes from 10.9.1.9: icmp_seq=1 ttl=64 time=116.335 ms
64 bytes from 10.9.1.9: icmp_seq=2 ttl=64 time=33.301 ms
```

If mDNS is **not** working, indicating you will have to use your IP directly, you will see something like this:

```
$ ping -c 3 spark-abcd.local
ping: cannot resolve spark-abcd.local: Unknown host
```

If none of these work, you'll need to:
- Log into your router's admin panel to find the IP Address
- Connect a display, keyboard, and mouse to check from the Ubuntu desktop

# Step 3. Test initial connection

Connect to your DGX Spark for the first time to verify basic connectivity:

```bash
# Connect using mDNS hostname (preferred)
ssh <YOUR_USERNAME>@<SPARK_HOSTNAME>.local
```

or

```bash
# Alternative: Connect using IP address
ssh <YOUR_USERNAME>@<DEVICE_IP_ADDRESS>
```

Replace placeholders with your actual values:
- `<YOUR_USERNAME>`: Your DGX Spark account name
- `<SPARK_HOSTNAME>`: Device hostname without `.local` suffix
- `<DEVICE_IP_ADDRESS>`: Your device's IP address

On first connection, you'll see a host fingerprint warning. Type `yes` and press Enter,
then enter your password when prompted.

# Step 4. Verify remote connection

Once connected, confirm you're on the DGX Spark device:

```bash
# Check hostname
hostname
# Check system information
uname -a
# Exit the session
exit
```

# Step 5. Use SSH tunneling for web applications

To access web applications running on your DGX Spark, use SSH port
forwarding. In this example we'll access the DGX Dashboard web application.

> [!NOTE]
> DGX Dashboard runs on localhost, port 11000.

Open the tunnel:

```bash
# local port 11000 → remote port 11000
ssh -L 11000:localhost:11000 <YOUR_USERNAME>@<SPARK_HOSTNAME>.local
```

After establishing the tunnel, access the forwarded web app in your browser: [http://localhost:11000](http://localhost:11000)

# Step 6. Next steps

With SSH access configured, you can:
- Open persistent terminal sessions: `ssh <YOUR_USERNAME>@<SPARK_HOSTNAME>.local`.
- Forward web application ports: `ssh -L <local_port>:localhost:<remote_port> <YOUR_USERNAME>@<SPARK_HOSTNAME>.local`.
