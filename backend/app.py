from flask import Flask, request, Response
import json
import re
import pymongo

app = Flask(__name__)

mongo = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo["CPSC5200-WQ"]
address_collection = db["Addresses"]

addr_formats = None


# construct a Flask Response object
def get_response(code, content):
	return Response(json.dumps(content), status=code, mimetype="application/json")


# load address formats from a file
def load_formats():
	global addr_formats

	file = open('addresses2.json', encoding='utf-8')
	addr_formats = json.load(file)
	file.close()


# get the address format for a specific ISO code
def get_format(country):
	if addr_formats is None:
		load_formats()

	if country not in addr_formats:
		return None

	return addr_formats[country]


# verify that the provided address matches the format of the country provided
def verify_address(address, country_code):
	# make sure that the country matches the format guidelines
	match = re.match(r'[A-Z]{2}', country_code, flags=0)
	if not match:
		print("ERROR: Invalid ISO country!")
		return False

	addr_format = get_format(country_code)

	# make sure that the format is present
	if addr_format is None:
		print("Country is not present in configuration file!")
		return False

	# make sure that this field isn't something that isn't in the format
	for field in address:
		if field not in addr_format and field != "Country":
			print("extra field present", field)
			return False

	for field in addr_format.keys():
		# make sure that we are not missing required fields
		if field not in address and addr_format[field] != "":
			print("missing field", field)
			return False

		# if the format has required values, check against those
		if isinstance(addr_format[field], dict):
			if not address[field] in addr_format[field].keys():
				print("not matching options", address[field])
				return False

		# otherwise, check against the provided regex if field not required
		elif addr_format[field] != "":
			regex = addr_format[field]
			if not re.match(regex, str(address[field]), flags=0):
				print("not matching regex", address[field])
				return False

	return True


@app.route('/addresses', methods=['POST'])
def insert_address():
	if not request.json:
		return get_response(400, {"message": "Failed to insert address", "result": "No request body."})
	data = request.json

	num_inserted = 0
	num_failed = 0
	for address in data:
		if "Country" not in address:
			num_failed += 1
			continue

		is_valid = verify_address(address, address["Country"])

		if is_valid:
			address_collection.insert_one(address)
			num_inserted += 1
		else:
			num_failed += 1

	return get_response(200, {"message": "Success", "result": "Inserted "+str(num_inserted)+" addresses. "+str(num_failed)+" not inserted."})


@app.route('/addresses')
def get_addresses():
	t_list = []
	for item in address_collection.find({}, {"_id": 0}):
		t_list.append(item)

	return get_response(200, {"message": "Success", "result": t_list})


@app.route('/addresses/<string:country>')
def get_by_country(country):
	addr_format = get_format(country)

	if addr_format is None:
		return get_response(400, {"message": "Failure", "result": "Country is not currently handled by this API."})

	t_list = []
	for item in address_collection.find({"Country": country}, {"_id": 0}):
		t_list.append(item)

	return get_response(200, {"message": "Success", "result": t_list})


if __name__ == '__main__':
	app.run()
