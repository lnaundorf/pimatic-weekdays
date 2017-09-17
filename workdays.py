import os
import json
from datetime import date
import holidays
import sys
import requests


class PimaticWorkday:
    def __init__(self):
        self.settings = self.read_settings()

    @staticmethod
    def read_settings():
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        settings_filename = os.path.join(__location__, "settings.json")

        with open(settings_filename) as settings_file:
            settings = json.load(settings_file)

        #print(settings)
        return settings

    def is_workday_today(self):
        today = date.today()
        weekday = today.isoweekday()

        # Check for weekend
        if weekday in (6,7):
            return False

        # Check for holiday
        try:
            holiday_class = getattr(holidays, self.settings['holidays']['country'])
        except AttributeError as e:
            print(e)
            return False

        holiday_days = holiday_class(years=today.year, prov=self.settings['holidays']['province'])

        return not today in holiday_days

    def do_pimatic_action(self, deviceId, actionName):
        pimatic_settings = self.settings['pimatic']
        url = "%s/api/device/%s/%s" %(pimatic_settings['host'], deviceId, actionName)
        response = requests.get(url, auth=(pimatic_settings['username'], pimatic_settings['password']), verify=False)
        if response.status_code != requests.codes.ok:
            print("Error while calling '%s'. Status code: %s" % (url, response.status_code))
            return False

        response_json = response.json()
        #print(response_json)
        success = response_json and response_json.get('success', False)
        if success:
            return True
        else:
            print("Error while calling '%s'. Response: %s" % (url, response.text))
            return False

    def do_action_on_workday(self, deviceId, actionName):
        if not self.is_workday_today():
            print("No workday today")
            return

        print("Today is workday. Execute action '%s' for deviceId '%s'" % (actionName, deviceId))
        self.do_pimatic_action(deviceId, actionName)


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 3:
        print("Usage: %s deviceId actionName" % args[0])
        sys.exit(0)

    deviceId = args[1]
    actionName = args[2]

    PimaticWorkday().do_action_on_workday(deviceId, actionName)