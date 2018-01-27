This is a simple script I call from cron to control a Z-wave switch that in turn controls the electric engine heater of my car.

Based on the time I configure that I want to leave home, it will turn
on the heater at an appropriate time depending on outside temperature. 

This way a bit of energy is saved, as it's only when it's really cold that
the heater should run for any extended period of time. 
See https://www.calix.se/en/support/faq 

It's used together with my [Home Assistant](https://home-assistant.io)
installation. The cron job calls the Home Assistant API to turn on and
off switches, and to check outside temperature.

This is a quite stupid little script that I wrote since I have not yet
found the time to learn enough about Home Assistant to do it all
inside the UI and backend.

Install by running `python setup.py install` in a virtualenv on some
machine. I run it from cron using the following:

```
* 0-7 * * mon /opt/engineheater/bin/start_engineheater --verbose --homeassistant-url https://localhost --toggle-switch input_boolean.auto_peugeot sensor.humidity_5_1 switch.peugeot_switch 06:15
```

The above command line is instructing the script to:

* Talk to Home Assistant at http://localhost
* Check the outside temperature by asking for the value of sensor.humidity_5_1 (it will ask for a V_TEMP attribute)
* If the outside temperature is such that it's time to turn on the heater, do so by turning on switch.peugeot_switch via HA.
* Time the heater such that it has been running for an appropriate time when I leave at 06:15 using the french-made car
  with a brand that is very hard to spell.
* Do this check once a minute from midnight until 07:00. 
* Only do the above if the input_boolean.auto_peugeot is on. 

Be aware that everything happens in the timezone of the server, not in the timezone set in Home Assistant.

See `start_engineheater --help` for further details. 

Now when I'm done with all this, I really should put it all in the HA UI instead. 


