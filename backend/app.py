from flask import Flask, request, Response
from flask_cors import CORS
import json
import re
import pymongo

app = Flask(__name__)
CORS(app)

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
def get_format(country=None):
	if addr_formats is None:
		load_formats()

	# return all formats if no country specified
	if country is None:
		return addr_formats

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

	addr_format = addr_format['format']

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


# allow the user to read address formats, and provide accessibility for frontend
@app.route('/formats', methods=['GET'])
def get_formats():
	return get_response(200, {"result": get_format()})


# allow the user to insert an address following country formats
@app.route('/addresses', methods=['POST'])
def insert_address():
	if not request.json:
		return get_response(400, {"result": "No request body."})
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

	return get_response(200, {"result": "Inserted "+str(num_inserted)+" addresses. "+str(num_failed)+" not inserted."})


# allow the user to retrieve all stored addresses
@app.route('/addresses')
def get_addresses():
	query = {}
	for arg in request.args:
		data = request.args.get(arg)
		query[arg] = {"$regex": ".*"+data+".*"}

	t_list = []
	for item in address_collection.find(query, {"_id": 0}).limit(10):
		t_list.append(item)

	return get_response(200, {"result": t_list})


# allow the user to search based on a country specific format
@app.route('/addresses/<string:country>')
def get_by_country(country):
	addr_format = get_format(country)

	if addr_format is None:
		return get_response(400, {"result": "Country is not currently handled by this API."})

	query = {"Country": country}
	for field in addr_format:
		arg = request.args.get(field)
		if arg is not None:
			query[field] = {"$regex": ".*"+arg+".*"}

	t_list = []
	for item in address_collection.find(query, {"_id": 0}).limit(10):
		t_list.append(item)

	return get_response(200, {"result": t_list})


if __name__ == '__main__':
	app.run()
