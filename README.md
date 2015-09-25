# python-cloud-monitor

A daemon that will listen to the littleBits cloud streaming API service and will inform you via slack when your bits come on or offline.

* install via ```sudo python setup.py install```
* edit ```cloud_monitor_credentials.cfg``` with the relevant credentials
* move ```cloud_monitor_credentials.cfg``` to ```~/.cloud_monitor_credentials.cfg``` (in your home directory)
* execute ```cloud-monitor```

To further daemonize this script, you can copy the following upstart script to ```/etc/init/cloud-monitor.conf``` and then the service can be started with ```service cloud-monitor start```:

```#!upstart
description "littleBits cloud monitor"

start on startup
stop on shutdown

respawn

exec start-stop-daemon -c <username> --start --chdir "/usr/local/bin/" --exec "/usr/local/bin/cloud-monitor```
