#!/bin/env/python

from bs4 import BeautifulSoup
import geocoder
import requests
import re

INSPECTION_DOMAIN = "http://info.kingcounty.gov/"
INSPECTION_PATH = "/health/ehs/foodsafety/inspections/Results.aspx"


INSPECTION_PARAMS = {
    'Output': 'W',
    'Business_Name': '',
    'Business_Address': '',
    'Longitude': '',
    'Latitude': '',
    'City': '',
    'Zip_Code': '',
    'Inspection_Type': 'All',
    'Inspection_Start': '',
    'Inspection_End': '',
    'Inspection_Closed_Business': 'A',
    'Violation_Points': '',
    'Violation_Red_Points': '',
    'Violation_Descr': '',
    'Fuzzy_Search': 'N',
    'Sort': 'H'
}


def get_inspection_page(**kwargs):
    url = INSPECTION_DOMAIN + INSPECTION_PATH
    params = INSPECTION_PARAMS.copy()
    for key, value in kwargs.items():
        if key in INSPECTION_PARAMS:
            params[key] = value
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.content, resp.encoding


def parse_source(html, encoding='utf-8'):
    parsed = BeautifulSoup(html, from_encoding=encoding)
    return parsed


def load_inspection_page(name):
    with open(name, 'r') as fh:
        content = fh.read()
    return content, 'utf-8'


def has_two_tds(elem):
    is_tr = elem.name == 'tr'
    td_children = elem.find_all('td', recursive=False)
    has_two = len(td_children) == 2
    return is_tr and has_two


def restaurant_data_generator(html):
    id_finder = re.compile(r'PR[\d]+~')
    return html.find_all('div', id=id_finder)


def clean_data(td):
    return unicode(td.text).strip(" \n:-")


def extract_restaurant_metadata(elem):
    restaurant_data_rows = elem.find('tbody').find_all(
        has_two_tds, recursive=False
    )
    rdata = {}
    current_label = ''
    for data_row in restaurant_data_rows:
        key_cell, val_cell = data_row.find_all('td', recursive=False)
        new_label = clean_data(key_cell)
        current_label = new_label if new_label else current_label
        rdata.setdefault(current_label, []).append(clean_data(val_cell))
    return rdata


def is_inspection_data_row(elem):
    is_tr = elem.name == 'tr'
    if not is_tr:
        return False
    td_children = elem.find_all('td', recursive=False)
    has_four = len(td_children) == 4
    this_text = clean_data(td_children[0]).lower()
    contains_word = 'inspection' in this_text
    does_not_start = not this_text.startswith('inspection')
    return is_tr and has_four and contains_word and does_not_start


def get_score_data(elem):
    inspection_rows = elem.find_all(is_inspection_data_row)
    total = inspections = highest = 0
    for row in inspection_rows:
        score = clean_data(row.find_all('td')[2])
        intvalue = int(score)
        inspections += 1
        total += intvalue
        highest = intvalue if intvalue > highest else highest
    if inspections == 0:
        average = 0
    else:
        average = total / inspections

    return {u'Average Score': average, u'Inspections Total': inspections, u'Highest Score': highest}


def get_geojson(result):
    address = " ".join(result.get('Address', ''))
    if not address:
        return None
    geocoded = geocoder.google(address)
    return geocoded.json


def result_generator(count):
    use_params = {
        'Inspection_Start': '03/02/2013',
        'Inspection_End': '03/02/2015',
        'Zip_Code': '98109'
    }
    #html_content, encoding = get_inspection_page(**use_params)
    html_content, encoding = load_inspection_page('inspection_page.html')
    parsed = parse_source(html_content, encoding)
    content_col = parsed.find('td', id="contentcol")
    data_list = restaurant_data_generator(content_col)
    for data_div in data_list[:count]:
        metadata = extract_restaurant_metadata(data_div)
        inspection_data = get_score_data(data_div)
        metadata.update(inspection_data)
        yield metadata


if __name__ == '__main__':
    for result in result_generator(10):
        geojson = get_geojson(result)
        print geojson
