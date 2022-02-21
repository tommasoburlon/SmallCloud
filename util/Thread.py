import json

class Thread:
	def __init__(self):
		self.id      = None
		self.title   = None
		self.user_id = None
		self.type = Thread.getType()
	
	def json_parse(self, j):
		if 'id' in j:
			self.id = (j['id'])
		if 'user_id' in j:
			self.user_id = (j['user_id'])
		if 'title' in j:
			self.title = (j['title'])
		if 'type' not in j or j['type'] != self.type:
			return False
		return True
	
	def json(self):
		return 	{'id' : self.id, 'title' : self.title, 'user_id' : self.user_id, 'type' : self.type}
		
	def serialize(self):
		return json.dumps(self.json())
	
	@staticmethod
	def deserialize(text):
		ret = Thread()
		ret.json_parse(json.loads(text))
		return ret
		
	@staticmethod
	def getType():
		return 1
