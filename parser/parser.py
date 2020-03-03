import json
import sys
import re


def get_format(country_iso):
    country_iso = country_iso.upper()

    # make sure that the country matches format guidelines
    match = re.match(r'[A-Z]{2}', country_iso, flags=0)
    if not match:
        print("ERROR: Invalid ISO country!")
        exit(1)

    with open('address.json', encoding='utf-8') as file:
        data = json.load(file)
        countries = data['options']

        # check if the country exists in the configuration file
        if country_iso not in [country['iso'] for country in countries]:
            print("Country is not present in configuration file!")
            exit(1)

        for country in countries:
            if country['iso'] == country_iso:
                return country['fields']


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Need a country ISO as argument")
        exit(1)

    print(get_format(sys.argv[1]))
