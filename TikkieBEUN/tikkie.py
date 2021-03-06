from time import time
import jwt
import requests

url = "https://api-sandbox.abnamro.com/v1/tikkie/platforms"


def post(auth, key, url, payload):
	headers = {'Authorization': "Bearer " + auth}
	headers['API-Key'] = key
	p = requests.post(url, json=payload, headers=headers)
	return p.json()

def get(auth, key, url):
	headers = {'Authorization': "Bearer " + auth, 'API-Key': key}
	p = requests.get(url, headers=headers)
	return p.json()

#unsure
def post_platform(auth, key, name, phone, mail, share=False):
	payload = {'name': name, 'phoneNumber': phone, 'email': mail}
	payload['platformUsage'] = 'PAYMENT_REQUEST_FOR_MYSELF'
	response = post(auth, key, url, payload)
	print(response)
	return response['platformToken']

#works
def get_platform(auth, key):
	response = get(auth, key, url)
	return response[0]['platformToken'] # er kan toch maar een platform zijn()

# works
def post_user(auth, key, platform, name, phone, iban, label):
	link = '/'.join([url, platform, 'users'])
	payload = {'name': name, 'phoneNumber': phone, 'iban': iban}
	payload['bankAccountLabel'] = label
	response = post(auth, key, link, payload)
	return (response['userToken'], response['bankAccounts'][0]['bankAccountToken'])

#works
def get_user(auth, api, platform):
	link = '/'.join([url, platform, 'users'])
	data = get(auth, api, link)
	# print(data)
	return data[0] 

#works
def post_payment(auth, api, platform, user, bank, value, desc, curr='EUR'):
	link = '/'.join([url, platform, 'users',
					user, 'bankaccounts', bank,
					'paymentrequests'])
	payload = {'amountInCents': int(value * 100), 'currency': curr, 'description': desc}
	response = post(auth, api, link, payload)
	return response['paymentRequestUrl']

def get_payments(auth, api, plat, user, offs, limit, start=False, end=False):
	headers = {'Authorization': "Bearer " + auth}
	headers['API-Key'] = api
	link = '/'.join([url, plat, 'users', user, 'paymentrequests'])
	query = {'offset': offs, 'limit': limit}
	if start:
		query['fromDate'] = start
	if end:
		query['toDate'] = end
	p = requests.get(link, headers=headers, params=query )
	return p.json()

def get_payment(auth, api, platform, user, payment)
	link = '/'.join([url, plat, 'users', user, 'paymentrequests', payment])
	data = get(auth, api, link)
	return response.json()

def user_check(user_json, auth, key, platform, name, phone, iban, label):
	post_user(auth, key, platform, name, phone, mail, iban, label)
	# todo add checking

#works
def tikkie_auth(issuer):
	with open('private_rsa.pem', 'r') as file:
	    private_key = file.read()

	with open('key-secret', 'r') as file:
	    key = file.readline()
	    secret = file.readline()
	
	key, secret = key[:-1], secret[:-1]

	url = "https://api-sandbox.abnamro.com/v1/oauth/token"

	exp = int(time() + 15 * 60)
	nbf = int(time())
	aud = "https://auth-sandbox.abnamro.com/oauth/token"
	payload = {"exp": exp, "nbf": nbf, "iss": issuer, "sub": key, "aud": aud}
	headers = {"API-Key": key, "Content-Type": "application/x-www-form-urlencoded"}
	
	signature = jwt.encode(payload, private_key, algorithm="RS256").decode()
	data = {'client_assertion': signature, 'scope': 'tikkie'}
	data['client_assertion_type'] = 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer'
	data['grant_type'] = 'client_credentials'
	p = requests.post(url, data=data, headers=headers)

	response = p.json()
	return response['access_token'], key

# wip
def tikkie_start(auth, api, name, mail, phone, share, iban, label):
	plat_json = get_platform(auth, api)

	user_json = get_user(auth, api, platform)
	user, bank = user_check(user_json)

	return platform, user, bank

def get_tikkie(contacts, auth, api, platform, user, bank):
	desc = 'Ontdebben'
	for key in contacts:
		value = contacts[key]['debt']
		contacts[key]['link'] = post_payment(auth, api, platform, user, bank,
											 value , desc)
	return contacts
