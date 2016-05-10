# Pilights
A repository for some electronics programming on the raspberry pi for a museum exhibit

# Running

The code is to be run on a raspberry pi - the current functionality is limited to detecting an event from an
IR Break Beam Sensor. Some means of representing the appropriate circuit will hopefully be added soon.

Checkout the repository, cd into the directory and, with an appropriate circuit connected via the GPIO, run:

```bash
sudo python3 detector.py
```

# Setup

This section documents the expected requirements for setting up the raspberry pi for the neopixel control to work.
For the moment this is based on
[this instructable](http://www.instructables.com/id/RasPi-w-Fadecandy-driver-WS2811WS2812-Addressable-/?ALLSTEPS)

```bash
sudo apt-get -y install git

git clone git://github.com/scanlime/fadecandy
cd fadecandy/server
make submodules
make
sudo mv fcserver /usr/local/bin/
```

Now create the json config in ```/usr/local/etc/fcserver.json``` with something like the following (needs updating
for the actual layout once determined):

```json
{
  "listen": [null, 7890],
  "verbose": true,
  "color": {
    "gamma": 2.5,
    "whitepoint": [1.0, 1.0, 1.0]
  },

  "devices": [
    {
      "type": "fadecandy",
      "serial": "ABCDEFGHIJKLMNOP",
      "map": [
        [0, 0, 0, 60],
        [0, 60, 64, 60],
        [0, 120, 128, 60],
        [0, 180, 192, 60],
        [0, 240, 256, 60],
        [0, 300, 320, 60],
        [0, 360, 384, 60],
        [0, 420, 448, 60]
      ]
    }
  ]
}
```

Now edit ```/etc/rc.local``` (using ```sudo``` if required) to organise the appropriate startup and add the
following before the ```exit 0```:

```bash
/usr/local/bin/fcserver /usr/local/etc/fcserver.json > /var/log/fcserver.log 2>&1 &
```

At this point, you should probably restart to test the setup and ensure the fcserver is up.

Once back up, tail the log and then plug in your fadecandy to get the device serial number:

```bash
tail -f /var/log/fcserver.log
```

This should show something like:
```
[1462395828:0326] NOTICE: Server listening on *:7890
USB device Fadecandy (Serial# XXXXXXXXXXXXXXXX, Version 1.07) has no matching configuration. Not using it.
```

and you should edit ```/usr/local/etc/fcserver.json``` to specify that as the serial string for the device.

Additional setup for the Raspberry Pi might include setting up wireless connectivity:

 * Add a wireless dongle - using the Desktop's WiFi Config may be easiest for this.
 * Enabling ssh via ```sudo raspi-config```
 * Allowing ssh by computer name through ```sudo apt-get -y install netatalk```

Given an appropriate circuit, you should now be able to run the example programs from the fadecandy project. For instance:

```bash
cd fadecandy/examples/python
python chase.py
```

Obviously I am choosing a Python example as it is my intention to use Python for this project.
