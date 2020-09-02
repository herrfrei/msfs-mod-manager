import datetime
import json
import urllib.request
import datetime

import lib.config as config


def get_version(appctxt):
    """Returns the version of the application"""
    try:
        with open(appctxt.get_resource("base.json"), "r") as fp:
            data = json.load(fp)
        return "v{}".format(data["version"])
    except Exception as e:
        return "v??"


def check_version(appctxt):
    """Returns the release URL if a new version is installed. Otherwise,
    returns False"""
    time_format = "%Y-%m-%d %H:%M:%S"

    # first try to read from the config file
    succeed, value = config.get_key_value(config.LAST_VER_CHECK_KEY)
    if succeed:
        try:
            # check if last successful version check was less than a day ago.
            # If so, skip
            last_check = datetime.datetime.strptime(value, time_format)
            if last_check > (datetime.datetime.now() - datetime.timedelta(days=1)):
                return False
        except ValueError:
            pass

    # open the remote url
    url = "https://api.github.com/repos/NathanVaughn/msfs-mod-manager/releases/latest"

    try:
        page = urllib.request.urlopen(url)
    except Exception as e:
        return

    # parse the json
    data = page.read()
    data = data.decode("utf-8")

    try:
        parsed_data = json.loads(data)
        remote_version = parsed_data["tag_name"]
    except:
        return False

    # write the config file back out
    config.set_key_value(
        config.LAST_VER_CHECK_KEY,
        datetime.datetime.strftime(datetime.datetime.now(), time_format),
    )

    # check if remote version is newer than local version
    if remote_version > get_version(appctxt):
        # if so, return release url
        return parsed_data["html_url"]
    else:
        return False