import json

class User:
	def __init__(self):
		self.username = None
		self.password = None
		self.id       = None
		self.type     = User.getType()
		
	def json_parse(self, j):
		if 'username' in j:
			self.username = j['username']
		if 'password' in j:
			self.password = j['password']
		if 'id' in j:
			self.id       = (j['id'])
		if 'type' not in j or j['type'] != self.type:
			return False
		return True
		
	def json(self):
		return {'username' : self.username, 'password' : self.password, 'id' : self.id, 'type' : self.type}
		
	def serialize(self):
		return json.dumps(self.json())
		
	@staticmethod
	def deserialize(text):
		ret = User()
		ret.json_parse(json.loads(text))
		return ret
	
	@staticmethod
	def getType():
		return 0;
