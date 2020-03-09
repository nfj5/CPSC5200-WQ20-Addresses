#AddressAPI Backend

An API for storing, retrieving, and updating addresses in many different country formats.

Addresses are stored in a MongoDB collection, verifying via address formats stored in the `addresses2.json` file.

Running the code
---
Install required packages via `pip install -r requirements.txt`.

Run the API with `python -m flask run`. You should receive output letting you know that the server
is running on localhost:5000.