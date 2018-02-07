import uuid
import os.path
import logging

import tornado.escape
import tornado.ioloop
import tornado.web
from tornado.concurrent import Future
from tornado import gen
from tornado.options import define, options, parse_command_line

define("port", default=9999, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")


class MessageBuffer(object):
	def __int__(self):
		self.waiters = set()
		self.cache =[]
		self.cache_size = 200

	def wait_for_message(self, cursor=None):
		result_future = Future()
		if cursor:
			new_count = 0
			for msg in reversed(self.cache):
				if msg["id"] == cursor:
					break
				new_count += 1
			if new_count:
				result_future.set_result(self.cache[-new_count:])
				return result_future
		self.waiters.add(result_future)
		return result_future

	def cancel_wait(self, future):
		self.waiters.remove(future)
		future.set_result([])

	def new_message(self, message):
		logging.info("Sending new message to %r listeners", len(self.waiters))
		for future in self.waiters:
			future.set_result(message)
		self.waiters = set()
		self.cache.extend(message)
		if len(self.cache) > self.cache_size:
			self.cache = self.cache[-self.cache_size:]

global_message_buffer = MessageBuffer()

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("index.html", messages=global_message_buffer.cache)

class MessageNewHandler(tornado.web.RequestHandler):
	def post(self):
		message = {
			"id": str(uuid.uuid4()),
			"body": self.get_argument("body")
}

		message["html"] = tornado.escape.to_basestring(
			self.render_string("message.html", message=message))
		if self.get_argument("next", None):
			self.redirect(self.get_argument("next"))
		else:
			self.write(message)

		global_message_buffer.new_message([message])


class MessageUpdateHandler(tornado.web.RequestHandler):
	@gen.coroutine
	def post(self):
		cursor = self.get_argument("cursor", None)
		self.future = global_message_buffer.wait_for_message(cursor=cursor)
		message = yield self.future
		if self.request.connection.stream.closed():
			return
		self.write(dict(message=message))

	def on_connection_close(self):
		global_message_buffer.cancel_wait(self.future)


def main():
	parse_command_line()
	app = tornado.web.Application(
		[
			(r"/", MainHandler),
			(r"/a/message/new", MessageNewHandler),
			(r"/a/message/update", MessageUpdateHandler),
			],
		cookie_secret = "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
		timplate_path=os.path.join(os.path.dirname(__file__), "templates"),
		static_path = os.path.join(os.path.dirname(__file__), "static"),
		xsrf_cookies = True,
		debug = options.debug,
)
	app.listen(options.port)
	tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
	main()

