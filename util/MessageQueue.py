import pika
import sys
import uuid

class MessageQueue:
	def __init__(self, hostname, username, password):
		self.username = username
		self.password = password
		self.hostname = hostname
		self.connection = None
		self.verbose = True
		self.resetConnection()
		
		result = self.channel.queue_declare(queue='', exclusive=True)
		self.callback_queue = result.method.queue
		self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)
		
	def resetConnection(self):
		try:
			credentials = pika.PlainCredentials(self.username, self.password)
			self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.hostname, 5672, "/", credentials))
			self.channel    = self.connection.channel()
			print("[INFO MESSAGE] RabbitMQ service enabled")
		except:
			e = sys.exc_info()[0]
			print("[ERROR MESSAGE] Impossible to connect to rabbitMQ, error = ", e)
			self.connection = None
	
	def callbackWrapper(self, callback, queue, ch, method, props, body):
		if self.verbose is True:
			print("[EVENT MESSAGE] receiving message from: ", queue, ", body: ", body)
			sys.stdout.flush()
		response = callback(queue, body)
		self.channel.basic_publish(exchange='',routing_key=props.reply_to,properties=pika.BasicProperties(correlation_id = props.correlation_id), body=str(response))
		self.channel.basic_ack(delivery_tag=method.delivery_tag)
    	
	def consumeJobs(self, queues, callbacks):
		for q in queues:
			self.channel.queue_declare(queue = q)
		self.channel.basic_qos(prefetch_count=1)
		for i in range(len(queues)):
			fun = (lambda ch, method, props, body, bound_i=i : self.callbackWrapper(callbacks[bound_i], queues[bound_i], ch, method, props, body))
			self.channel.basic_consume(queue=queues[i], on_message_callback = fun)
		self.channel.start_consuming()
	
		
	def on_response(self, ch, method, props, body):
		if self.corr_id == props.correlation_id:
			self.response = body

	def sendJob(self, queueName, data):
		if self.verbose is True:
			print("[EVENT MESSAGE] sending message to: ", queueName, ", body: ", data)
			sys.stdout.flush()
	
		self.response = None
		self.corr_id = str(uuid.uuid4())
		self.channel.basic_publish(exchange='',routing_key=queueName,properties=pika.BasicProperties(reply_to=self.callback_queue,correlation_id=self.corr_id,),body=data)
		while self.response is None:
			self.connection.process_data_events()
		return self.response
        
	def __del__(self):
		if self.connection is not None:
			self.connection.close()
