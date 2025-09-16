# NOAA-at-Home

A custom Home Assistant integration to allows you to record and display satellite data. This is an attempt to add functionality similar to [Raspberry NOAA V2](https://github.com/jekhokie/raspberry-noaa-v2).

**Disclaimer:** This project is in active development and many of the advertised features are not working or not implemented yet.


# Features

- Ability to predict passes for any object in obit.
- Automatically schedule passes to be recorded with a SDR (RTL-SDR, Hack RF, ect.)
- Automatically decode data (like weather images) and display it on the dashboard.
- Push collected data and schedules of satellite passes to email, Discord, and more.


# Available service actions

**get_tle**

  Downloads TLEs for weather and amateur satellites from Celestrak and updates local files.
  

**schedule_passes**

  Schedules passes to be recorded for the selected satellite
