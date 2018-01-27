This is a simple script I call from cron to control a Z-wave switch that in turn controls the electric engine heater of my car.

Based on the time I configure that I want to leave home, it will turn
on the heater at an appropriate time depending on outside temperature.

It's used together with my [Home Assistant](https://home-assistant.io)
installation. The cron job calls the Home Assistant API to turn on and
off switches, and to check outside temperature.

This is a quite stupid little script that I wrote since I have not yet
found the time to learn enough about Home Assistant to do it all
inside the UI and backend.

Install by running `python setup.py install` in a virtualenv on some machine. I run it from cron using the following:

```
* 0-7 * * mon /opt/engineheater/bin/start_engineheater --verbose --homeassistant-url https://localhost sensor.humidity_5_1 switch.peugeot_switch 06:15
```

That tells the script that I want to leave home at 06:15 (be aware
that your server's timezone needs to be taken into account), and will
check temperature from midnight and forward to figure out when to turn
on the heater.

See `start_engineheater --help` for further details. 


