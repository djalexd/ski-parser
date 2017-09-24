#!/usr/bin/env python3
import requests
import hashlib
from lxml import html
import time
import json

base_url = 'https://www.bergfex.com'
visited = {}
resorts = []

def parse_ski_resort(url, html_contents):
    n = html_contents.xpath('//div[@class="heading heading-ne"]/h2/text()')
    # Try a different header
    if len(n) == 0:
        n = html_contents.xpath('//div[@class="heading heading-ne"]/h1/text()')
    h = html_contents.xpath('//div[@class="heading heading-ne"]/h3/text()')
    slopes_info = html_contents.xpath('//dl[@class="dd-dense"]/dt/text()')
    slopes_length = html_contents.xpath('//dl[@class="dd-dense"]/dd/text()')
    lift_counts = html_contents.xpath('//div[@class="anzahl"]/text()')
    lift_info = html_contents.xpath('//div[contains(@class, "icon")]/@title')
    return {
        'url': url,
        'name': n,
        'height': h,
        'slopes': {
            'info': slopes_info,
            'length': slopes_length
        },
        'lifts': {
            'info': lift_info,
            'counts': lift_counts
        }
    }

def visit_link(link):
    # Skip
    if link in visited:
        return None
    # Traverse
    full_url = "%s%s" % (base_url, link)
    print("Inspecting '%s'" % full_url)
    try:
        page = requests.get(full_url)
        visited[link] = True
        if page.status_code == requests.codes.ok:
            # parse response
            tree = html.fromstring(page.content)
            is_ski_identif = tree.xpath('//div[@id="donutchart"]')
            if is_ski_identif is None or len(is_ski_identif) is 0:
                # This is not a ski resort page, continue scaping
                # Check for contents
                other_resorts = tree.xpath('//div[contains(@class, "cols2")]//li/a/@href')
                print("Found %d 'resort' links" % len(other_resorts))
                for l in other_resorts:
                    visit_link(l)
                    time.sleep(0.2)
                
                # Check for any other regions and countries
                other_regions_or_countries = tree.xpath('//li[@class="hastotals"]/a/@href')
                print("Found %d links (currently %d resorts)" % (len(other_regions_or_countries), len(resorts)))
                for l in other_regions_or_countries:
                    visit_link(l)
                    time.sleep(0.1)
            else:
                # Parse elements
                resort = parse_ski_resort(full_url, tree)
                resorts.append(resort)
                print ("Found sky resort page - %s (currently %d resorts)" % (full_url, len(resorts)))
                # done, no more scraping
        else:
            return None
    except Exception:
        print("Some exception occured, ignoring %s" % full_url)

with open('resorts.json', 'w') as f:
    visit_link('/oesterreich/')
    json.dump(resorts, f)
