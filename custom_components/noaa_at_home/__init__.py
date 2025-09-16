import requests
import logging
import predict
import subprocess

import custom_components.noaa_at_home.utils

from datetime import datetime
from dataclasses import dataclass


DOMAIN = "noaa_at_home"

def setup(hass, config):
    _LOGGER = logging.getLogger("custom_components.noaa_at_home")

    # Get settings from Settings.yaml
    settings = utils.parse_yaml("/config/custom_components/noaa_at_home/Settings.yaml", Settings)

    #Set up satellite options in services.yaml
    sats = utils.parse_multi_doc_yaml("/config/custom_components/noaa_at_home/Sat_Settings.yaml", Sat_Settings)

    services_file = open("/config/custom_components/noaa_at_home/services.yaml", 'r')
    lines = services_file.readlines()
    services_file.close()

    # Delete old options if any
    i = 20
    while True:
        if not "-" in lines[i]:
            break
        del lines[i]
        i += 1

    # Add new options
    for i in range(len(sats)):
        lines.insert(i + 20, "            - \"" + sats[i].sat_name + "\"\n")

    services_file = open("/config/custom_components/noaa_at_home/services.yaml", 'w')
    services_file.writelines(lines)
    services_file.close()


    # Service to update the TLE files
    def update_tle(call):
        _LOGGER.info("Updating tle files")

        # Download weather sat TLEs and coppy to file
        weather_file = open("/config/custom_components/noaa_at_home/tle/Weather_TLE.txt", "w")

        response = requests.get("http://www.celestrak.org/NORAD/elements/weather.txt")

        if response.status_code == 200:
            weather_file.write(response.text)
            _LOGGER.info("Updated weather TLE")
        
        else:
            _LOGGER.warning("Failled to get weather TLE")

        weather_file.close()

        # Download amateur sat TLEs and coppy to file
        amateur_file = open("/config/custom_components/noaa_at_home/tle/Amateur_TLE.txt", "w")

        response = requests.get("http://www.celestrak.org/NORAD/elements/amateur.txt")

        if response.status_code == 200:
            amateur_file.write(response.text)
            _LOGGER.info("Updated amateur TLE")
        
        else:
            _LOGGER.warning("Failled to get amateur TLE")

        amateur_file.close()

    hass.services.register(DOMAIN, "update_tle", update_tle)
    

    # Schedule passes for the selected satellite
    def schedule_passes(call):
        satellite = call.data.get("satellite")

        _LOGGER.info(f"Scheduling passes for \"{satellite}\"")

        sats = utils.parse_multi_doc_yaml("/config/custom_components/noaa_at_home/Sat_Settings.yaml", Sat_Settings)
        
        if satellite == "ALL":
            for sat in sats:
                break
        else:
            settings = None
            for sat in sats:
                if sat.sat_name == satellite:
                    settings = sat
                    break

            if settings == None:
                _LOGGER.error(f"Could not find \"{satellite}\". Check \"Sat_Settings.yaml\" and restart HA")
                return

            tle = utils.get_tle(satellite)

            if tle == None:
                _LOGGER.warning(f"Could not find TLE for \"{satellite}\"")
                return

            _LOGGER.info(f"Found TLE:\n{tle}")

            nth_day = datetime.now() + datetime.timedelta(days=settings.days_to_schedule_passes - 1)

            passes = predict.transits(tle, (settings.latitude, settings.longitude, settings.altitude), datetime.now().timestamp(), datetime.datetime(nth_day.year, nth_day.month, nth_day.day).timestamp())

            _LOGGER.info(f"Found {len(passes)} passes")


    hass.services.register(DOMAIN, "schedule_passes", schedule_passes)


    return True


@dataclass
class Settings:
    latitude: float
    longitude: float
    altitude: int

    receiver_type: str

    days_to_schedule_passes: int

    enable_email_push: bool
    enable_email_schedule_push: bool
    email_push_address: str
    enable_discord_push: bool
    discord_webhook_url: str


@dataclass
class Sat_Settings:
    sat_name: str
    sat_sdr_device_id: int
    sat_record_freq: int
    sat_freq_offset: int
    sat_enable_bias_tee: bool
    sat_gain: float
    sat_sun_min_elevation: int

    sat_sat_min_elevation: int
