#!/usr/bin/env python
import requests
import json
from random import sample
from time import sleep
from string import lowercase, digits
from unicodedata import normalize


class BeefAPI:

	def __init__(self, opts=[]):
		self.host = "127.0.0.1" or opts.get(host)
		self.port = "3000" or opts.get(port)
		self.token = None
		self.url = "http://%s:%s/api/" % (self.host, self.port)
		self.login_url = self.url + "admin/login"
		self.hookurl = self.url + "hooks?token="
		self.mod_url = self.url + "modules?token="
		self.log_url = self.url + "logs?token="

	def random_url(self):
		url = "".join(sample(digits + lowercase, 8))
		return url

	def login(self, username, password):
		try:
			auth = json.dumps({"username": username, "password": password})
			r = requests.post(self.login_url, data=auth)
			data = r.json()

			if (r.status_code == 200) and (data["success"]):
				self.token = data["token"]  #Auth token
				return True
			elif r.status_code != 200:
				return False
		
		except Exception, e:
			print "beefapi ERROR: %s" % e

	def onlineSessions(self):
		return self.get_sessions("online", "session")

	def offlineSessions(self):
		return self.get_sessions("offline", "session")

	def onlineHosts(self):
		return self.get_sessions("online", "ip")

	def offlineHosts(self):
		return self.get_sessions("offline", "ip")

	def get_sessions(self, state, value):
		r = requests.get(self.hookurl).json()
		hooks = []
		try:
			for v in r["hooked-browsers"][state].items():
				hooks.append(str(v[1][value]))
				return hooks
		except Exception, e:
			print "beefapi ERROR: %s" % e

	def getModid(self, name): #Returns module id
		url = self.url + "%s" % (self.token)
		r = requests.get(url).json()
		try:
			for v in r.values():
				if v["name"] == name:
					return v["id"]
		except KeyError:
			print "beefapi ERROR: module '" + name + "' not found!"
			return None

	def getModname(self, id): #Returns module name
		url = self.url + "modules?token=%s" % (self.token)
		r = requests.get(url).json()
		try:
			for v in r.values():
				if v["id"] == id:
					return v["name"]
		except KeyError:
			print "beefapi ERROR: module '" + id + "' not found!"
			return None

	def host2session(self, ip): # IP => Session
		url = self.url + "hooks?token=%s" % (self.token)
		r = requests.get(url).json()
		try:
			for v in r["hooked-browsers"]["online"].items():
				if v[1]["ip"] == ip:
					return v[1]["session"]
				else:
					session = None
		
				if session == None:
					for v in r["hooked-browsers"]["offline"].items():
						if v[1]["ip"] == ip:
							return v[1]["session"]
						else:
							return None
	
		except KeyError:
			pass

	def session2host(self, session): # Session => IP
		url = self.url + "hooks?token=%s" % (self.token)
		r = requests.get(url).json()

		try:
			for v in r["hooked-browsers"]["online"].items():
				if v[1]["session"] == session:
					return v[1]["ip"]
				else:
					ip = None
		
				if ip == None:
					for v in r["hooked-browsers"]["offline"].items():
						if v[1]["session"] == session:
							return v[1]["ip"]
					else:
						return None
		except KeyError:
			pass

	def runModule(self, session, mod_id, options={}): #Executes a module on a specified session
		headers = {"Content-Type": "application/json", "charset": "UTF-8"}
		payload = json.dumps(options)
		url = self.url + "modules/%s/%s?token=%s" % (session, mod_id, self.token)
		return requests.post(url, headers=headers, data=payload).json()

	def moduleResult(self, session, mod_id, cmd_id):
		url = self.mod_url + "%s/%s/%s?token=%s" % (session, mod_id, cmd_id, self.token)
		return requests.get(url).json()
	
	def sessionInfo(self, session):  #Returns parsed information on a session
		url = self.url + "hooks/%s?token=%s" % (session, self.token)
		return requests.get(url).json()

	def logs(self):
		return requests.get(self.log_url + self.token).json()

	def sessionLogs(self, session):
		url = self.url + "logs/%s?token=%s" % (session, self.token)
		return requests.get(url).json()

	def listModules(self):
		return requests.get(self.mod_url + self.token).json()

	def moduleInfo(self, id):
		url = self.url + "modules/%s?token=%s" % (id, self.token)
		return requests.get(url).json()