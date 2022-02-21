from pymemcache.client.hash import HashClient
import pika
import dns
import dns.resolver
import mysql.connector
from MessageQueue import MessageQueue
from User import User
from Thread import Thread
from Comment import Comment
from Message import Message, ReturnCode
import sys


mydb = mysql.connector.connect(
  host="mysql.default.svc.cluster.local",
  user="root",
  password="password",
  database = "forum"
)

def fromRecordToObject(type, record):
	obj = None
	if type == User.getType():
		obj = User()
		obj.id       = record[0]
		obj.username = record[1]
		obj.password = record[2]
	elif type == Thread.getType():
		obj = Thread()
		obj.id       = record[0]
		obj.user_id  = record[1]
		obj.title    = record[2]
	elif type == Comment.getType():
		obj = Comment()
		obj.id        = record[0]
		obj.thread_id = record[1]
		obj.user_id   = record[2]
		obj.body      = record[3]
		obj.postDate  = str(record[4])
	return obj
		
def post_callback(queue, body):
	mess = Message.deserialize(body)
	
	if len(mess.contents) == 0:
		mess.ret_code = ReturnCode.NOARG
		return mess
	
	obj = mess.contents[0]
	
	sql = None
	val = None
	if obj.type == User.getType():
		sql = "INSERT INTO user (username, password) VALUES (%s, %s)"
		val = (obj.username, obj.password)
	elif obj.type == Thread.getType():
		sql = "INSERT INTO thread (user_id, title) VALUES (%s, %s)"
		val = (obj.user_id, obj.title)
	elif obj.type == Comment.getType():
		sql = "INSERT INTO comment (user_id, thread_id, body) VALUES (%s, %s, %s)"
		val = (obj.user_id, obj.thread_id, obj.body)
	else:
		mess.ret_code = ReturnCode.BADARG
		return mess.serialize()
	
	mycursor = mydb.cursor()
	mycursor.execute(sql, val)
	mydb.commit()
	
	obj.id = mycursor.lastrowid 
	return mess.serialize()

def get_callback(queue, body):
	mess = Message.deserialize(body)
	
	if len(mess.contents) == 0:
		mess.ret_code = ReturnCode.NOARG
		return mess
	
	obj = mess.contents[0]
	
	sql = None
	val = None
	if obj.type == User.getType():
		sql = "SELECT id, username, password FROM user WHERE id = %s LIMIT 1"
		val = (obj.id,)
	elif obj.type == Thread.getType():
		sql = "SELECT id, user_id, title FROM thread WHERE id = %s LIMIT 1"
		val = (obj.id,)
	elif obj.type == Comment.getType():
		sql = "SELECT id, thread_id, user_id, body, postDate FROM comment WHERE id = %s LIMIT 1"
		val = (obj.id,)
	else:
		mess.ret_code = ReturnCode.BADARG
		return mess.serialize()
	
	mycursor = mydb.cursor()
	mycursor.execute(sql, val)
	response = mycursor.fetchall()
	record = None
	for temp in response:
		record = temp
	if record is None:
		mess.contents = []
		return mess.serialize()
	
	obj = fromRecordToObject(obj.type, record)
		
	mess.contents[0] = obj
	
	return mess.serialize()
	
def put_callback(queue, body):
	mess = Message.deserialize(body)
	if len(mess.contents) == 0:
		mess.ret_code = ReturnCode.NOARG
		return mess
	
	obj = mess.contents[0]
	
	sql = None
	val = None
	if obj.type == User.getType():
		sql = "UPDATE user SET username = %s, password = %s WHERE id = %s"
		val = (obj.username, obj.password, obj.id)
	elif obj.type == Thread.getType():
		sql = "UPDATE thread SET title = %s WHERE id = %s"
		val = (obj.title, obj.id)
	elif obj.type == Comment.getType():
		sql = "UPDATE comment SET body = %s WHERE id = %s"
		val = (obj.body, obj.id)
	else:
		mess.ret_code = ReturnCode.BADARG
		return mess.serialize()
	
	mycursor = mydb.cursor()
	mycursor.execute(sql, val)

	mydb.commit()
	
	return mess.serialize()

def delete_callback(queue, body):
	mess = Message.deserialize(body)
	
	if len(mess.contents) == 0:
		mess.ret_code = ReturnCode.NOARG
		return mess
	
	obj = mess.contents[0]
	
	sql = None
	val = None
	if obj.type == User.getType():
		sql = "DELETE FROM user WHERE id = %s"
		val = (obj.id,)
	elif obj.type == Thread.getType():
		sql = "DELETE FROM thread WHERE id = %s"
		val = (obj.id,)
	elif obj.type == Comment.getType():
		sql = "DELETE FROM comment WHERE id = %s"
		val = (obj.id,)
	else:
		mess.ret_code = ReturnCode.BADARG
		return mess.serialize()
	
	mycursor = mydb.cursor()
	mycursor.execute(sql, val)
	mydb.commit()
	
	mess.contents = [];
	return mess.serialize()
	
def get_list_callback(queue, body):
	mess = Message.deserialize(body)
	
	if len(mess.contents) == 0:
		mess.ret_code = ReturnCode.NOARG
		return mess
	
	obj = mess.contents[0]
	mess.contents = []
	
	if obj.type == User.getType():
		sql = "SELECT * FROM user LIMIT 15 OFFSET %s"
		val = (15 * int(obj.id),)
	elif obj.type == Thread.getType():
		sql = "SELECT * FROM thread LIMIT 15 OFFSET %s"
		val = (15 * int(obj.id),)
	elif obj.type == Comment.getType():
		if obj.thread_id is not None:
			sql = "SELECT * FROM comment WHERE thread_id = %s ORDER BY postDate ASC LIMIT 15 OFFSET %s "
			val = (int(obj.thread_id), 15 * int(obj.id))
		elif obj.user_id is not None:
			sql = "SELECT * FROM comment WHERE user_id = %s ORDER BY postDate ASC LIMIT 15 OFFSET %s "
			val = (int(obj.user_id), 15 * int(obj.id))
		else:
			sql = "SELECT * FROM comment ORDER BY postDate DESC LIMIT 15 OFFSET %s "
			val = (15 * int(obj.id),)
	else:
		mess.ret_code = ReturnCode.BADARG
		return mess.serialize()
	
	mycursor = mydb.cursor()
	mycursor.execute(sql, val)
	response = mycursor.fetchall()
	for record in response:
		mess.contents.append(fromRecordToObject(obj.type, record))
		
	return mess.serialize()
	
if __name__ == "__main__":
	queue = MessageQueue("rabbitmq-service.default.svc.cluster.local", "guest", "guest")

	mydb = mysql.connector.connect(
	  host="mysql.default.svc.cluster.local",
	  user="root",
	  password="password",
	  database = "forum"
	)
	print("[INFO] db connected")
	sys.stdout.flush()
	
	queue.consumeJobs(["POST", "GET", "PUT", "DELETE", "GET LIST"], [post_callback, get_callback, put_callback, delete_callback, get_list_callback])


