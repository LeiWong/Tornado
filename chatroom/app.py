import time
import json

import tornado.ioloop
import tornado.web

data = [
	{"id":777, "content": "chat room test"}
]

class IndexHandler(tornado.web.RequestHandler):
	def get(self, *args, **kwargs):
		self.render("index.html")


class MessageHandler(tornado.web.RequestHandler):

	def get(self, *args, **kwargs):
		index = self.get_argument("index")
		index = int(index)
		if index == 0:
			self.write(json.dumps(data))
		else:
			self.write(json.dumps(data[index:]))


settings = {
	"template_path": "views",
	"static_path": "static",
}


application = tornado.web.Application([
	(r"/index.html", IndexHandler),
	(r"/msg.html", MessageHandler),
],
 **settings
)


if __name__ == "__main__":
	print("Starting server on 127.0.0.1:9090")
	application.listen(9090)
	tornado.ioloop.IOLoop.instance().start()

