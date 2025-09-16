import yaml
#import logging

from typing import Type, TypeVar


T = TypeVar('T')

#_LOGGER = logging.getLogger("custom_components.noaa_at_home")


def parse_yaml(filepath: str, t: Type[T]) -> T:
    doc = None

    with open(filepath, 'r') as f:
        doc = t(**yaml.safe_load(f))
    return doc


def parse_multi_doc_yaml(filepath: str, t: Type[T]) -> list[T]:
    doc_list = []

    with open(filepath, 'r') as f:
        for doc in yaml.safe_load_all(f):
            doc_list.append(t(**doc))
    return doc_list


def get_tle(satellite: str) -> str:
    tle = ""

    with open("/config/custom_components/noaa_at_home/tle/Weather_TLE.txt") as f:
        i = 0
        for line in f:
            if i % 3 == 0:
                if satellite in line:
                    tle = line
                    i = 0
                    for line in f:
                        tle += line
                        if i == 1:
                            return tle
                        i += 1
            i += 1

    if tle == None:
        with open("/config/custom_components/noaa_at_home/tle/Amateur_TLE.txt") as f:
            i = 0
        for line in f:
            if i % 3 == 0:
                if satellite in line:
                    tle = line
                    i = 0
                    for line in f:
                        tle += line
                        if i == 1:
                            return tle
                        i += 1
            i += 1

    return None



