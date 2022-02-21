import json
from User import User
from Thread import Thread
from Comment import Comment
from enum import Enum

class ReturnCode(Enum):
	OK = 1
	NOARG = 2
	BADARG = 3
	DBERR = 4
	
class Message:
	def __init__(self):
		self.contents = []	
		self.ret_code = ReturnCode.OK

	def json_parse(self, JSON):
		if 'code' in JSON:
			self.ret_code = ReturnCode(int(JSON['code']))
		
		if 'content' not in JSON:
			return
			
		vec = JSON['content']
		for record in vec:
			if 'type' in record:
				idx = int(record['type'])
				obj = None
				if idx == User.getType():
					obj = User()
				elif idx == Thread.getType():
					obj = Thread()
				elif idx == Comment.getType():
					obj = Comment()
				else:
					continue
				obj.json_parse(record)
				self.contents.append(obj)
	
	def json(self):
		ret = []
		for o in self.contents:
			ret.append(o.json())
		return {'code' : self.ret_code.value, 'content' : ret}
		
	def serialize(self):
		return json.dumps(self.json())
		
	def insert(self, obj):
		self.contents.append(obj)
		
	@staticmethod
	def deserialize(text):
		ret = Message()
		ret.json_parse(json.loads(text))
		return ret
	
