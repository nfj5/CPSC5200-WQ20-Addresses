import json
import sys


def get_format(country_iso):
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
