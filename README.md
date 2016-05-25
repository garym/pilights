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

Ensure git is installed:

```bash
sudo apt-get -y install git
```

Clone this repository if you do not already have a copy and initialise the FadeCandy submodule:

```bash
git clone git://github.com/garym/pilights
cd pilights
git submodule update --init
```

build the FadeCandy server
```bash
cd fadecandy/server
make submodules
make
sudo mv fcserver /usr/local/bin/
```

Now create the json config in ```/usr/local/etc/fcserver.json``` with something like the following.
The serial for the device is a placeholder which we will discover in a later step.
The map describes the mapping of each of the 8 outputs from the fadecandy to the pixels being controlled.
In the initial version of the exhibit we are using 6 of the outputs to control:

 1. an 8 pixel stick
 1. a 1/4 circle of 12
 1. a 1/4 circle of 12
 1. a 1/4 circle of 12
 1. a 1/4 circle of 12
 1. an 8 pixel stick

The map contained will allow us to treat all the pixels as a continuous range from 0 to 75 so we don't have to
consider an offset.

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
        [0, 0, 0, 8],
        [0, 8, 64, 15],
        [0, 23, 128, 15],
        [0, 38, 192, 15],
        [0, 53, 256, 15],
        [0, 68, 320, 8],
        [0, 76, 384, 60],
        [0, 136, 448, 60]
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

 * Add a wireless dongle - using the Desktop's WiFi Config may be easiest for this but it is also possible to edit the ```/etc/wpa_supplicant/wpa_supplicant.conf``` by hand.
 * Enabling ssh via ```sudo raspi-config```
 * Allowing ssh by computer name through ```sudo apt-get -y install netatalk```

Given an appropriate circuit, you should now be able to run the example programs from the fadecandy project. For instance:

```bash
cd fadecandy/examples/python
python chase.py
```

The current test pattern can be run through:
```bash
python display.py
```
