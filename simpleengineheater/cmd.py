import json
import datetime
import requests
import sys
from logging import basicConfig, getLogger, INFO, DEBUG
from argparse import ArgumentParser



def start_engineheater():
    basicConfig(level=INFO, stream=sys.stderr)

    log = getLogger(__name__)

    parser = ArgumentParser()
    parser.add_argument("sensor")
    parser.add_argument("switch")
    parser.add_argument("targettime")
    parser.add_argument("--extra-time", default=30, type=int)
    parser.add_argument("--homeassistant-url", default="http://localhost:8123")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--toggle-switch", help="Switch in Home Assistant that tells if we should do anything at all")

    args = parser.parse_args()

    if args.verbose:
        log.root.setLevel(DEBUG)

    if args.toggle_switch:
        toggle = requests.get("%s/api/states/%s" % (args.homeassistant_url, args.toggle_switch)).json()["state"]
        log.debug("toggle switch is in state %s" % toggle)
        if toggle == "off":
            log.debug("We are disabled by switch in UI. Bye!")
            return
                              

    current_temperature = float(requests.get("%s/api/states/%s" % (args.homeassistant_url, args.sensor)).json()["attributes"]["V_TEMP"])
    log.debug("Current temperature: %f" % current_temperature)

    switch_state = requests.get("%s/api/states/%s" % (args.homeassistant_url, args.switch)).json()["state"]
    log.debug("switch_state: %r" % switch_state)

    (hour, minute) = map(int, args.targettime.split(":"))

    now = datetime.datetime.now()
    targettime = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if switch_state == "off":
        heatingtime = _heatingtime(current_temperature)
        log.debug("Heating time is %r" % heatingtime)

        if heatingtime is None:
            log.debug("Too warm, not turning on engine heater")
            return

        if now < targettime and now + heatingtime > targettime:
            log.debug("Turning on engine heater for %d seconds" % heatingtime.seconds)
            requests.post("%s/api/services/homeassistant/turn_on"  % args.homeassistant_url,
                          headers={"Content-Type": "application/json"},
                          data=json.dumps({"entity_id": args.switch}))

    elif switch_state == "on":
        if now - targettime > datetime.timedelta(minutes=args.extra_time):
            log.debug("Turning off engine heater due to time out")
            requests.post("%s/api/services/homeassistant/turn_off" % args.homeassistant_url,
              headers={"Content-Type": "application/json"},
              data=json.dumps({"entity_id": args.switch}))


def _heatingtime(outside_temperature):
    if outside_temperature > 15:
        return None
    if outside_temperature > 0:
        return datetime.timedelta(hours=1)

    seconds_per_degree = 3600*3 / 20
    return datetime.timedelta(hours=1, seconds=seconds_per_degree*-1*outside_temperature)








