import json

class Comment:
	def __init__(self):
		self.id        = None
		self.thread_id = None
		self.user_id   = None
		self.body      = None
		self.postDate  = None
		self.type      = Comment.getType()
	
	def json_parse(self, j):
		if 'id' in j:
			self.id = j['id']
		if 'user_id' in j:
			self.user_id = (j['user_id'])
		if 'thread_id' in j:
			self.thread_id = (j['thread_id'])
		if 'body' in j:
			self.body = j['body']
		if 'postDate' in j:
			self.postDate = j['postDate']
		if 'type' not in j or j['type'] != self.type:
			return False
		return True
	
	def json(self):
		return 	{'id' : self.id, 'thread_id' : self.thread_id, 'user_id' : self.user_id, 'body' : self.body, 'postDate' : self.postDate, 'type' : self.type}
		
	def serialize(self):
		return json.dumps(self.json())
	
	@staticmethod
	def deserialize(text):
		ret = Comment()
		ret.json_parse(json.loads(text))
		return ret
	
	@staticmethod
	def getType():
		return 2
