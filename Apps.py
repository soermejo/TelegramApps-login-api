import requests, random, sys
from lxml import html


class Apps:

	"""
	This class will automatically create api_key and api_hash if they are not created yet and/or 
	will return them if they are already created!
	"""

	def __init__(self, phone_number, callback=None, app_name=None, short_name=None):
		self.phone_number = phone_number
		self.app_name = app_name
		self.short_name = short_name
		self.callback = callback
		self.initializer()

	def initializer(self):
		self.base_url = "https://my.telegram.org"
		self.session = requests.Session()
		self.stored_data = {}

		if not self.app_name:
			self.app_name = ''.join(random.choice('abcdefghilmnopqrstuvz') for _ in range(10))
		if not self.short_name:
			self.short_name = ''.join(random.choice('abcdefghilmnopqrstuvz') for _ in range(5))
		if self.callback:
			self.pwd = self.callback
		else:
			self.pwd = input('Insert code: ')


	def send_password(self):
		entry_point = "/auth/send_password"
		url = self.base_url+entry_point
		data = {"phone":self.phone_number}
		res = self.session.post(url, data=data)
		if res.ok:
			self.stored_data.update(res.json()) # Add hash to stored data
			return True
		else:
			print("Failed to send_password!")
			print(self.stored_data)
			sys.exit(0)

	def login(self):
		entry_point = "/auth/login"
		url = self.base_url+entry_point
		self.stored_data['pwd'] = self.pwd()
		data = {
			"phone": self.phone_number,
			"random_hash": self.stored_data['random_hash'],
			"password": self.stored_data['pwd']
		}
		res = self.session.post(url, data=data)
		if res.ok:
			return True
		else:
			print("Login Failed!")
			print(self.stored_data)
			sys.exit(0)

	def create_apps(self):
		entry_point = "/apps/create"
		url = self.base_url+entry_point
		
		data = {
			"hash": self.stored_data['hash'],
			"app_title": self.app_name,
			"app_shortname": self.short_name,
			"app_platform": "android"
		}

		res = self.session.post(url, data=data)
		if res.ok:
			print('Apps created!')
			return self.get_credentials(res.text)
		else:
			print('Error on creating apps:')
			print(self.stored_data)
			sys.exit(0)

	def get_apps(self):
		entry_point = "/apps"
		url = self.base_url+entry_point
		res = self.session.get(url)
		tree = html.fromstring(res.content)
		_hash = tree.xpath('//*[@id="app_create_form"]/input/@value')
		if not _hash:
			print('Detected apps credentials already created!')
			res = self.session.get(url)
			return self.get_credentials(res.text)
		else:
			print('Detected apps credentials not created yet! creating now...')
			_hash = _hash[0]
			self.stored_data['hash'] = _hash
			return self.create_apps()

	def get_credentials(self, html_code):
		tree = html.fromstring(html_code)
		api_id = tree.xpath('//*[@id="app_edit_form"]/div[1]/div[1]/span/strong/node()')[0]
		api_hash = tree.xpath('//*[@id="app_edit_form"]/div[2]/div[1]/span/node()')[0]
		print("API_ID: %s, API_HASH: %s" % (api_id, api_hash))
		self.stored_data['api_id'] = api_id
		self.stored_data['api_hash'] = api_hash
		return True


	def auto(self):
		self.send_password()
		self.login()
		self.get_apps()
		if 'api_id' in self.stored_data:
			return [self.stored_data['api_id'], self.stored_data['api_hash']]
		else:
			return False
