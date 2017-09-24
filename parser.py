#!/usr/bin/env python3
import json
import requests
import os
import sys

def parse_name(name):
    if len(name) != 1:
        raise ValueError("Invalid name - multiple named, expected 1: %s" % name)
    return name[0].strip()

def parse_single_height(raw):
    """
        Input: '17m' or '17' or '   20m    '
    """
    raw = raw.strip()
    if "m" in raw:
        raw = raw[:raw.index("m")]
    raw = raw.replace(".", "")
    return int(raw)


def parse_height(raw):
    if len(raw) != 1:
        raise ValueError("Invalid height object - multiple heights, expected 1: %s" % raw)
    raw = raw[0]
    raw = raw.strip()
    parts = raw.split('-')
    if len(parts) != 2:
        raise ValueError('Invalid height object - doesn\'t contain 2 tokens')
    else:
        return {
            'min': parse_single_height(parts[0]),
            'max': parse_single_height(parts[1])
        }


def parse_single_length(raw):
    raw = raw.strip()
    if "km" in raw:
        return float(raw[:raw.index("km")])
    else:
        return 0.0


def adjust_slopes(slope_obj):
    if 'info' not in slope_obj or 'length' not in slope_obj:
        raise ValueError('Invalid slope object - structure')

    info = slope_obj['info']
    length = slope_obj['length']
    if len(info) != len(length):
        raise ValueError('Invalid slope object - cardinality')
    if len(length) != 5:
        raise ValueError('Invalid slope object - not all values')
    return {
        'easy': parse_single_length(length[0]),
        'medium': parse_single_length(length[1]),
        'difficult': parse_single_length(length[2]),
        'freeride': parse_single_length(length[3]),
        'total': parse_single_length(length[4]),
    }

def adjust_lifts(lifts_obj):
    if 'info' not in lifts_obj or 'counts' not in lifts_obj:
        raise ValueError('Invalid lifts object - structure')

    info = lifts_obj['info']
    counts = lifts_obj['counts']
    if len(info) != len(counts):
        raise ValueError('Invalid lifts object - cardinality')
    if len(info) != 5:
        raise ValueError('Invalid lifts object - not all values')
    d = dict()
    for idx, val in enumerate(info):
        d[val.lower()] = int(counts[idx])
    return d

def adjust(resort):
    try :
        return {
            'url': resort['url'],
            'name': parse_name(resort['name']),
            'heights': parse_height(resort['height']),
            'slopes': adjust_slopes(resort['slopes']),
            'lifts': adjust_lifts(resort['lifts'])
        }, None
    except ValueError as err:
        return None, err, resort['url']

def distance_from(origin, destination):
    payload = {
        'origins': origin,
        'destinations': destination,
        'key': os.environ['GOOGLE_API_KEY']
    }

    page = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json", params=payload)
    results = page.json()
    return results['rows'][0]['elements'][0]['distance']['value'] / 1000

with open('resorts.json') as input:
    resorts_results = [adjust(r) for r in json.load(input)]
    parsed = 0
    errors_in_parsing = 0
    for resort_parse_result in resorts_results:
        if resort_parse_result[1] is None:
            parsed += 1
        else:
            errors_in_parsing += 1
    print("Parsed %d, Parsed with errors %d" % (parsed, errors_in_parsing))

    f = [e[0] for e in resorts_results if e[1] is None]
    f = [e for e in f if e['heights']['min'] > 1000]
    f = [e for e in f if e['heights']['max'] > 2500]
    f = [e for e in f if e['slopes']['total'] > 80]
    f = [e for e in f if e['slopes']['medium'] > 40]

    print("Found %d resorts" % len(f))
    for resort in f:
        try:
            from = os.environ['']
            resort['distance_from_berlin'] = distance_from(sys.argv[1], resort['name'])
        except KeyError:
            resort['distance_from_berlin'] = 0.0

    with open('resorts_parsed.json', 'w') as output:
        json.dump(f, output)
