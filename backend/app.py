from flask import Flask, request, Response
from flask_cors import CORS
from flask_restplus import Api, Resource, fields
from bson.errors import InvalidId
from bson.objectid import ObjectId
import json
import re
import pymongo

VERSION = "0.1.0"

flask_app = Flask(__name__)
CORS(flask_app, resources={r"/*": {"origins": "*"}}, headers='Content-Type')
flask_app.config.from_object(__name__)

app = Api(
		app=flask_app,
		version=VERSION,
		title="AddressAPI",
		description="API for storing/updating/retrieving world addresses.")

namespace = app.namespace('addresses', description='Main API interface')
format_namespace = app.namespace('formats', description='Address format endpoints')

mongo = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo["CPSC5200-WQ"]
address_collection = db["Addresses"]

addr_formats = None

# region Helper Code


# construct a Flask Response object
def get_response(code, content):
	return Response(json.dumps(content), status=code, mimetype="application/json")


# format the address object for sending as JSON
def json_format(address):
	address['_id'] = str(address['_id'])
	return address


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


example_address = app.model('AddressPostModel', {
	'Country': fields.String(required=True, example='CA'),
	'Address1': fields.String(example='14 Albertson Lane'),
	'Address2': fields.String(example='Apartment 240'),
	'City': fields.String(example='Vancouver'),
	'Province': fields.String(example='BC'),
	'PostalCode': fields.Integer(example=35421)
})

example_address_put = app.model('AddressPutModel', {
	'Address2': fields.String(example='Apartment 243')
})

example_response = app.model('AddressPostResponseModel', {
	'Country': fields.String(required=True, example='CA'),
	'Address1': fields.String(example='14 Albertson Lane'),
	'Address2': fields.String(example='Apartment 240'),
	'City': fields.String(example='Vancouver'),
	'Province': fields.String(example='BC'),
	'PostalCode': fields.Integer(example=35421),
	'_id': fields.String(example='5e6096e3b0cbe6aa74b93c19')
})

example_response_put = app.inherit('AddressPutResponseModel', example_response, {
	'Address2': fields.String(example='Apartment 243')
})

# endregion


# allow the user to read address formats, and provide accessibility for frontend
@format_namespace.route('/')
class GetFormats(Resource):
	def get(self):
		return get_response(200, get_format())

# region Address API Endpoints


@namespace.route('/')
class Addresses(Resource):
	# allow the user to retrieve all stored addresses
	@app.doc(responses={200: "Success", 400: "Invalid request format"})
	def get(self):
		query = {}
		for arg in request.args:
			data = request.args.get(arg)
			query[arg] = {"$regex": ".*" + data + ".*"}

		t_list = []
		for item in address_collection.find(query).limit(10):
			t_list.append(json_format(item))

		return get_response(200, t_list)

	# allow the user to insert an address following country formats
	# @app.doc(responses={200: "Success", 400: "Invalid request format"}, example=example_response)
	@app.response(200, 'Success', example_response)
	@app.response(400, 'Invalid request format')
	@app.expect(example_address)
	def post(self):
		if not request.json:
			return get_response(400, {"error": "No request body."})
		address = request.json

		if "Country" not in address:
			return get_response(400, {"error": "No country specified."})

		is_valid = verify_address(address, address["Country"])

		if not is_valid:
			return get_response(400, {"error": "Address format is not valid for the specified country."})

		insertion = address_collection.insert_one(address)
		address["_id"] = str(insertion.inserted_id)

		return get_response(200, json_format(address))


@namespace.route('/<string:address_id>')
class AddressById(Resource):
	# get a specific address based upon the identifier
	@app.param('address_id', 'The specified address identifier')
	@app.doc(responses={200: "Success", 400: "Invalid request format"})
	def get(self, address_id):
		try:
			result = address_collection.find({"_id": ObjectId(address_id)})
			item = {}
			if result.count() == 1:
				item = json_format(result[0])
			return get_response(200, item)
		except InvalidId:
			return get_response(400, {"error": "Invalid ObjectId sequence"})

	# allow the user to update the specified address
	@app.param('address_id', 'The specified address identifier')
	@app.response(200, 'Success', example_response_put)
	@app.response(400, 'Invalid request format')
	@app.expect(example_address_put)
	def put(self, address_id):
		if not request.json:
			return get_response(400, {"error": "No request body."})
		address = request.json

		try:
			# see if the address exists in the database for updating
			to_update = address_collection.find_one({"_id": ObjectId(address_id)})
			if not to_update:
				return get_response(400, {"error": "Address has not yet been created."})

			# make sure that we are only updating fields that are part of the format
			curr_format = get_format(to_update['Country'])['format']
			for field in list(address):
				if field not in curr_format or field == 'Country':
					del address[field]
				else:
					to_update[field] = address[field]

			if len(address) == 0:
				return get_response(400, {"error": "No valid fields to update."})

			# update the item and return the new address
			address_collection.update_one({"_id": ObjectId(address_id)}, {"$set": address}, upsert=False)
			return get_response(200, json_format(to_update))
		except InvalidId:
			return get_response(400, {"error": "Invalid ObjectId sequence"})


# allow the user to search based on a country specific format
@namespace.route('/country/<string:country>')
class GetByCountry(Resource):
	@app.param('country', 'The country to search in')
	@app.doc(responses={200: "Success", 400: "Invalid request format"})
	def get(self, country):
		addr_format = get_format(country)

		if addr_format is None:
			return get_response(400, {"result": "Country is not currently handled by this API."})

		query = {"Country": country}
		for field in addr_format:
			arg = request.args.get(field)
			if arg is not None:
				query[field] = {"$regex": ".*" + arg + ".*"}

		t_list = []
		for item in address_collection.find(query).limit(10):
			t_list.append(json_format(item))

		return get_response(200, t_list)

# endregion


if __name__ == '__main__':
	flask_app.run()
