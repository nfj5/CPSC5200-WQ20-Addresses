import json
import sys
import re


def get_format(country_iso):
    country_iso = country_iso.upper()
    match = re.match(r'[A-Z]{2}', country_iso, flags=0)
    if not match:
        print("ERROR: Invalid ISO country!")
        exit(1)
    with open('address.json', encoding='utf-8') as file:
        data = json.load(file)
        countries = data['options']

        for country in countries:
            if country['iso'] == country_iso:
                return country['fields']


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Need a country ISO as argument")
        exit(1)

    format = get_format(sys.argv[1])
    print(format)
