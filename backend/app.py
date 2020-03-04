from flask import Flask, request
import json
import re
import pymongo

app = Flask(__name__)

mongo = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo["CPSC5200-WQ"]
address_collection = db["Addresses"]


@app.route('/')
def hello_world():
    return 'Hello World!'


# verify that the provided address matches the format of the country provided
def verify_address(address, country_code):
    # make sure that the country matches the format guidelines
    match = re.match(r'[A-Z]{2}', country_code, flags=0)
    if not match:
        print("ERROR: Invalid ISO country!")
        return False

    with open('addresses2.json', encoding='utf-8') as file:
        data = json.load(file)

        # make sure that the country is present
        if country_code not in data.keys():
            print("Country is not present in configuration file!")
            return False

        # try to find the country
        for country in data.keys():
            if country == country_code:
                format = data[country]

                for field in format.keys():
                    # make sure that we are not missing required fields
                    if not field in address and format[field] != "":
                        print("missing field", field)
                        return False

                    # if the format has required values, check against those
                    if isinstance(format[field], dict):
                        if not address[field] in format[field].keys():
                            print ("not matching options", address[field])
                            return False

                    # otherwise, check against the provided regex
                    else:
                        regex = format[field]
                        if not re.match(regex, address[field], flags=0):
                            print ("not matching regex", address[field])
                            return False

                return True

    return False


@app.route('/addresses', methods=['POST'])
def insert_address():
    if not request.json:
        return {"message": "Failed to insert address", "result": "No request body."}
    data = request.json

    num_inserted = 0
    num_failed = 0
    for address in data:
        is_valid = verify_address(address, address["Country"])

        if is_valid:
            address_collection.insert_one(address)
            num_inserted += 1
        else:
            num_failed += 1

    return {"message": "Success", "result": "Inserted "+str(num_inserted)+" addresses. "+str(num_failed)+" not inserted."}

if __name__ == '__main__':
    app.run()
