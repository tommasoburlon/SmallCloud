from pymemcache.client.hash import HashClient
import dns
import dns.resolver
import sys

class CacheHandler:
	def __init__(self, hostname):
		self.hostname = hostname;
		self.cache = None
		self.verbose = True
		self.updateServer()
	
	def updateServer(self):
		try:
			result = dns.resolver.resolve(self.hostname, 'A')
		except:
			print("[ERROR CACHE] IPs of the cache servers not found")
			self.cache = None
			return
		
		ips = []
		print("[INFO CACHE] updating cache-server, ips: ", end = "")
		for ipval in result:
			currIP = ipval.to_text() + ":11211"
			ips.append(currIP)
			print(currIP, end = ", ")
		print("")
			
		self.cache = HashClient(ips)
	
	def set(self, key, value):
		if self.cache is None:
			return
		self.cache.set(key, value)
	
	def get(self, key):
		if self.cache is None:
			return None
		try:
			sys.stdout.flush()
			res = self.cache.get(key)
			if self.verbose is True:
				if res is None:
					print("[EVENT CACHE] cache miss (key: ", key, ")")
				else:
					print("[EVENT CACHE] cache hit (key: ", key, ")")
				sys.stdout.flush()
			return res
		except:
			print("[ERROR CACHE] cache server not found")
			sys.stdout.flush()
			self.updateServers()
			return None
			
	def delete(self, key):
		if self.cache is None:
			return None
		try:
			self.cache.delete(key)
		except:
			print("[ERROR CACHE] cache server not found")
			sys.stdout.flush()
			self.updateServers()
			return None
			
