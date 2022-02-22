from MessageQueue import MessageQueue
from CacheHandler import CacheHandler
from flask import Flask, render_template, redirect, request, session, abort
from flask_session import Session
from User import User
from Thread import Thread
from Comment import Comment
from Message import Message, ReturnCode
import json
import sys


THREAD_PAGES = 5
COMMENT_PAGES = 5
COMMENT_IN_THREAD = 5

cache = CacheHandler("cache-service.default.svc.cluster.local")
queue = MessageQueue("rabbitmq-service.default.svc.cluster.local", "guest", "guest")

app = Flask("forum")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
print("[INFO] flask server initializated")



@app.route("/")
def index():
	print("[INFO] variables THREAD_PAGES: ", THREAD_PAGES, ", COMMENT_PAGES: ", COMMENT_PAGES, ", COMMENT_IN_THREAD: ", COMMENT_IN_THREAD, ", cache: ", str(cache.cache))
	return ""
	

######## USER HANDLE #########
		
@app.route("/users/<page>", methods = ['GET'])
def getUsers(page):
	
	mess = Message()
	user = User()
	user.id = page
	mess.insert(user)

	mess = Message.deserialize(queue.sendJob("GET LIST", mess.serialize()))
	
	return json.dumps(mess.json()['content'])
	
@app.route("/user", methods = ['POST'])
def postUser():
	request_data = request.get_json(force = True)
	user = User()
	user.json_parse(request_data)
	
	if user.username == None or user.password == None:
		abort()
	
	mess = Message()
	mess.insert(user)
	
	response = queue.sendJob("POST", mess.serialize())
	
	mess = Message.deserialize(response)
	
	if mess.ret_code is not ReturnCode.OK:
		print("[ERROR] message code: ", mess.ret_code)
		sys.stdout.flush()
		abort(500)
	else:
		user    = mess.contents[0]
		cache.set("user_" + str(user.id), user.serialize())
		return json.dumps({'status' : 'OK', 'user' : user.json()})

@app.route("/user/<id>", methods = ['GET'])
def getUser(id):
	user = cache.get("user_" + id)
	if user is None:
		
		mess = Message()
		user = User()
		user.id = id
		user.username = None
		user.password = None
		mess.insert(user)
		mess = Message.deserialize(queue.sendJob("GET", mess.serialize()))
		
		if mess.ret_code is ReturnCode.OK and len(mess.contents) == 1:
			user = mess.contents[0]
			cache.set("user_" + id, user.serialize())
		else:
			abort(404)
	else:
		user = User.deserialize(user)
	return user.serialize()
	
@app.route("/user/<id>", methods = ['PUT'])
def putUser(id):
	request_data = request.get_json(force = True)
	user = User()
	user.json_parse(request_data)
	
	if user.username == None or user.password == None:
		abort()
	user.id = id
	
	mess = Message()
	mess.insert(user)
	
	response = queue.sendJob("PUT", mess.serialize())
	
	mess = Message.deserialize(response)
	
	if mess.ret_code is not ReturnCode.OK:
		print("[ERROR] message code: ", mess.ret_code)
		sys.stdout.flush()
		abort(500)
	else:
		user    = mess.contents[0]
		cache.set("user_" + str(user.id), user.serialize())
		return json.dumps({'status' : 'OK', 'user' : user.json()})

@app.route("/user/<id>", methods = ['DELETE'])
def delUser(id):
	mess = Message()
	user = User()
	user.id = id
	mess.insert(user)
	mess = Message.deserialize(queue.sendJob("DELETE", mess.serialize()))
		
	return json.dumps({"response" : mess.ret_code.value})
	
######### THREAD HANDLE ############
def flushThreads():
	for i in range(THREAD_PAGES):
		cache.delete("thread_page_" + str(i))
			
@app.route("/threads/<page>", methods = ['GET'])
def getThreads(page):
	cacheMiss = False
	ret = None
	if int(page) < THREAD_PAGES:
		ret = cache.get("thread_page_" + str(page))
	
	if ret == None:
		cacheMiss = True
		mess = Message()
		thread = Thread()
		thread.id = page
		mess.insert(thread)
				
		ret = queue.sendJob("GET LIST", mess.serialize())
	
	message.deserialize(ret)
	
	if int(page) < THREAD_PAGES and cacheMiss is True:
		cache.set("thread_page_" + str(page), ret)
		
	return json.dumps(mess.json()['content'])

@app.route("/thread", methods = ['POST'])
def postThread():
	request_data = request.get_json(force = True)
	thread = Thread()
	thread.json_parse(request_data)
	
	if thread.title == None or thread.user_id == None:
		abort()
	
	mess = Message()
	mess.insert(thread)
	
	response = queue.sendJob("POST", mess.serialize())
	mess = Message.deserialize(response)
	
	if mess.ret_code is not ReturnCode.OK:
		print("[ERROR] message code: ", mess.ret_code)
		sys.stdout.flush()
		abort(500)
	else:
		flushThreads()
		thread    = mess.contents[0]
		cache.set("thread_" + str(thread.id), thread.serialize())
		return json.dumps({'status' : 'OK', 'thread' : thread.json()})

@app.route("/thread/<id>", methods = ['GET'])
def getThread(id):
	thread = cache.get("thread_" + id)
	if thread is None:
		
		mess = Message()
		thread = Thread()
		thread.id = id
		thread.title = None
		thread.user_id = None
		mess.insert(thread)
		mess = Message.deserialize(queue.sendJob("GET", mess.serialize()))
		
		if mess.ret_code is ReturnCode.OK and len(mess.contents) == 1:
			thread = mess.contents[0]
			cache.set("thread_" + id, thread.serialize())
		else:
			abort(404)
	else:
		thread = Thread.deserialize(thread)
	return thread.serialize()
	
@app.route("/thread/<id>", methods = ['PUT'])
def putThread(id):
	request_data = request.get_json(force = True)
	thread = Thread()
	thread.json_parse(request_data)
	
	if thread.title == None:
		abort()
	thread.user_id = None
	thread.id = id
	
	mess = Message()
	mess.insert(thread)
	
	response = queue.sendJob("PUT", mess.serialize())
	mess = Message.deserialize(response)
	
	if mess.ret_code is not ReturnCode.OK:
		print("[ERROR] message code: ", mess.ret_code)
		sys.stdout.flush()
		abort(500)
	else:
		flushThreads()
		thread    = mess.contents[0]
		cache.set("thread_" + str(thread.id), thread.serialize())
		return json.dumps({'status' : 'OK', 'thread' : thread.json()})

@app.route("/thread/<id>", methods = ['DELETE'])
def delThread(id):
	mess = Message()
	thread = Thread()
	thread.id = id
	mess.insert(thread)
	mess = Message.deserialize(queue.sendJob("DELETE", mess.serialize()))
	
	flushThreads()
	return json.dumps({"response" : mess.ret_code.value})
	
############ COMMENT HANDLE #############
def flushCommentPages(thread_id):
	for i in range(COMMENT_IN_THREAD):
		cache.delete("comment_" + str(i) + "_thread_" + str(thread_id))
	for i in range(COMMENT_PAGES):
		cache.delete("comment_page_" + str(i))
		
@app.route("/threadComments/<thread_id>/<page>", methods = ['GET'])
def getCommentsInThread(thread_id, page):
	ret = None
	cacheMiss = False
	if int(page) < COMMENT_IN_THREAD:
		ret = cache.get("comment_" + str(page) + "_thread_" + str(thread_id))
	
	if ret == None:
		cacheMiss = True
		mess = Message()
		comment = Comment()
		comment.id = page
		comment.thread_id = thread_id
		mess.insert(comment)

		ret = queue.sendJob("GET LIST", mess.serialize())
		
	mess = Message.deserialize(ret)
	
	if int(page) < COMMENT_IN_THREAD and cacheMiss is True:
		cache.set("comment_" + str(page) + "_thread_" + str(thread_id), ret)
		
	return json.dumps(mess.json()['content'])

@app.route("/lastComments/<page>", methods = ['GET'])
def getLastComments(page):
	ret = None
	cacheMiss = False
	if int(page) < COMMENT_IN_THREAD:
		ret = cache.get("comment_page_" + str(page))
	
	if ret is None:
		cacheMiss = True
		mess = Message()
		comment = Comment()
		comment.id = page
		mess.insert(comment)

		ret = queue.sendJob("GET LIST", mess.serialize())
		
	mess = Message.deserialize(ret)
	
	if int(page) < COMMENT_IN_THREAD:
		ret = cache.set("comment_page_" + str(page), ret)
	return json.dumps(mess.json()['content'])
	
@app.route("/comment", methods = ["POST"])
def postComment():
	request_data = request.get_json(force = True)
	comment = Comment()
	comment.json_parse(request_data)
	
	if comment.body == None or comment.user_id == None or comment.thread_id == None:
		abort()
	
	mess = Message()
	mess.insert(comment)
	
	response = queue.sendJob("POST", mess.serialize())
	mess = Message.deserialize(response)
	
	if mess.ret_code is not ReturnCode.OK:
		print("[ERROR] message code: ", mess.ret_code)
		sys.stdout.flush()
		abort(500)
	else:
		flushCommentPages(comment.thread_id)
		comment    = mess.contents[0]
		cache.set("comment_" + str(comment.id), comment.serialize())
		return json.dumps({'status' : 'OK', 'comment' : comment.json()})

@app.route("/comment/<id>", methods = ["GET"])
def getComment(id):
	comment = cache.get("comment_" + id)
	if comment is None:
		
		mess = Message()
		comment = Comment()
		comment.id = id
		comment.body = None
		comment.user_id = None
		comment.thread_id = None
		mess.insert(comment)
		mess = Message.deserialize(queue.sendJob("GET", mess.serialize()))
		
		if mess.ret_code is ReturnCode.OK and len(mess.contents) == 1:
			comment = mess.contents[0]
			cache.set("comment_" + id, comment.serialize())
		else:
			abort(404)
	else:
		comment = Comment.deserialize(comment)
	return comment.serialize()
	
@app.route("/comment/<id>", methods = ["PUT"])
def putComment(id):
	request_data = request.get_json(force = True)
	comment = Comment()
	comment.json_parse(request_data)
	
	if comment.body == None:
		abort()
	comment.user_id = None
	comment.thread_id = None
	comment.id = id
	
	mess = Message()
	mess.insert(comment)
	
	response = queue.sendJob("PUT", mess.serialize())
	mess = Message.deserialize(response)
	
	if mess.ret_code is not ReturnCode.OK:
		print("[ERROR] message code: ", mess.ret_code)
		sys.stdout.flush()
		abort(500)
	else:
		#flushCommentPages(comment.thread_id)
		comment    = mess.contents[0]
		cache.set("comment_" + str(comment.id), comment.serialize())
		return json.dumps({'status' : 'OK', 'comment' : comment.json()})

@app.route("/comment/<id>", methods = ['DELETE'])
def delComment(id):
	mess = Message()
	comment = Comment()
	comment.id = id
	mess.insert(comment)
	mess = Message.deserialize(queue.sendJob("DELETE", mess.serialize()))
		
	return json.dumps({"response" : mess.ret_code.value})
	
if __name__ == "__main__":
	app.run(debug = False, host = "0.0.0.0", port = 15000)
	
	
	
	
