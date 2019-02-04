import os
import pytz
import json
import datetime
import calendar
import requests
import sys
from logging import basicConfig, getLogger, INFO, DEBUG
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

def start_engineheater():
    parser = ArgumentParser(description="Automatically start engine heater based on outside temperature",
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("sensor", help="Sensor in HA that gives us current temperature")
    parser.add_argument("hass_group", help="Name of group in HA that contains switch, input_select and input_datetime")
    parser.add_argument("--time-zone", default="Europe/Stockholm", help="Timezone of HA, as configured in configuration.yaml")
    parser.add_argument("--extra-time", default=30, type=int)
    parser.add_argument("--homeassistant-url", default="http://localhost:8123")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--hass-access-token", help="Path to file with Home Assistant access token",
                        default=os.path.expanduser("~/.hass-access-token"))

    args = parser.parse_args()

    basicConfig(level=DEBUG if args.verbose else INFO)
    log = getLogger(__name__)

    try:
        access_token = open(args.hass_access_token).read().strip()
    except IOError as e:
        log.error("Unable to read HASS Access Token from %s. Please create one in HASS UI and write it to that file" % args.hass_access_token)
        sys.exit(1)

    session = requests.Session()
    session.headers.update({'Authorization': "Bearer %s" % access_token})

    utc_tz = pytz.timezone("UTC")
    hass_tz = pytz.timezone(args.time_zone)

    hass_now = datetime.datetime.now(hass_tz)

    group = session.get("%s/api/states/%s" % (args.homeassistant_url, "group."+args.hass_group)).json()
    # Filter out the name of the input_select. We don't care in which order they were defined in the group.
    [run_select] = [entity for entity in group['attributes']['entity_id'] if entity.startswith('input_select')]

    run = session.get("%s/api/states/%s" % (args.homeassistant_url, run_select)).json()['state']

    dow = hass_now.weekday()
    if run == "Working Days" and dow > 4:
        log.debug("Run only on Working Days. Today is %s" % calendar.day_name[dow])
        return
    elif run == "False":
        log.debug("Don't run at all")
        return


    [departure_time_entity] = [entity for entity in group['attributes']['entity_id'] if entity.startswith('input_datetime')]
    [switch_entity] = [entity for entity in group['attributes']['entity_id'] if
                       entity.startswith('switch') or entity.startswith('input_boolean')]

    switch_state = session.get("%s/api/states/%s" % (args.homeassistant_url, switch_entity)).json()["state"]
    log.debug("switch_state: %r" % switch_state)

    departure_time = session.get("%s/api/states/%s" % (args.homeassistant_url, departure_time_entity)).json()['state']

    (departure_hour, departure_minute) = map(int, departure_time.split(":")[:2])

    departure_time = hass_now.replace(hour=departure_hour, minute=departure_minute, second=0, microsecond=0)

    if switch_state == "on":
        if hass_now - departure_time > datetime.timedelta(minutes=args.extra_time):
            log.debug("Turning off engine heater due to time out")
            session.post("%s/api/services/homeassistant/turn_off" % args.homeassistant_url,
              headers={"Content-Type": "application/json"},
              data=json.dumps({"entity_id": switch_entity}))
            return

    if departure_time < hass_now:
        log.debug("Time is in the past. Assuming you mean tomorrow")
        departure_time += datetime.timedelta(days=1)

    log.debug("Departure time is %r" % departure_time)

    current_temperature = float(session.get("%s/api/states/%s" % (args.homeassistant_url, args.sensor)).json()["state"])
    log.debug("Current temperature: %f" % current_temperature)

    if switch_state == "off":
        heatingtime = _heatingtime(current_temperature)
        log.debug("Heating time is %r" % heatingtime)

        if heatingtime is None:
            log.debug("Too warm, not turning on engine heater")
            return

        if hass_now < departure_time and hass_now + heatingtime > departure_time:
            log.debug("Turning on engine heater for %d seconds" % heatingtime.seconds)
            session.post("%s/api/services/homeassistant/turn_on"  % args.homeassistant_url,
                          headers={"Content-Type": "application/json"},
                          data=json.dumps({"entity_id": switch_entity}))



def _heatingtime(outside_temperature):
    if outside_temperature > 15:
        return None
    if outside_temperature > 0:
        return datetime.timedelta(hours=1)

    seconds_per_degree = 3600*3 / 20
    return datetime.timedelta(hours=1, seconds=seconds_per_degree*-1*outside_temperature)








