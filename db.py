# coding:utf-8
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options  # self-define command line module
import json
from tornado.web import RequestHandler
import torndb

# self-define port by command line
tornado.options.define("port",type=int,default=8000,help="define port")
class BaseHandler(RequestHandler):

    def prepare(self):
        if self.request.headers.get('Content-Type','').startswith('application/json'):
            self.data = (json.loads(self.request.body))
    
    def write_error(self,status_code,**kwargs):
       #when request is error,the Handler will call the mothod write_error
        self.write('<h1>200,我好想你[苏打绿]</h1>')
        self.write('<title>%d,%s</title>'%(status_code,kwargs.get("title","")))
        self.write('<p>%s</p>'%kwargs.get("content",""))


class IndexHandler(BaseHandler):
    def get(self):
        data =self.application.db.get("select ui_name from it_user_info where ui_user_id=1")
        self.write(data['ui_name'])
    def post(self):
        name = self.get_argument("name")
        passwd = self.get_argument("passwd")
        mobile = self.get_argument("mobile")
        sql = "insert into it_user_info(ui_name,ui_passwd,ui_mobile) values(%(name)s,%(passwd)s,%(mobile))"
        try:
            ret =self.application.db.execute(sql,name=name,passwd=passwd,mobile=mobile)
        except Exception as e:
            print e
            return self.write("%s"%e)
        self.write("OK,%s"%ret)

class HouseHandler(BaseHandler):
    def get(self):
        ui_user_id = self.get_argument("uid")
        print ui_user_id
        sql = "select * from it_user_info inner join it_house_info on ui_user_id=hi_user_id where ui_user_id=%s"
        try:
            ret = self.application.db.query(sql,ui_user_id)
        except Exception as e:
            return self.write({"errNo":1,"errMe":"DB error","data":[]})
        houses = []
        if ret:
            for l in ret:
              house = {
                      "uname":l["ui_name"],
                      "umobile":l["ui_mobile"],
                }
              houses.append(house)
        self.write({"errNo":0,"errMe":"OK","data":houses})


class Application(tornado.web.Application):
    def __init__(self,*args,**kwargs):
        super(Application,self).__init__(*args,**kwargs)
        self.db = torndb.Connection(
                host="127.0.0.1",
                database="itcast",
                user="root",
                password="mysql"
                )
if __name__ == '__main__':
    # parse self-define options
    tornado.options.parse_command_line()
    app = Application([
        (r'/',IndexHandler),
        (r'/house',HouseHandler)
        ],debug=True)
    # app.listen(8000)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(tornado.options.options.port)
    # http_server.bind(8000)
    # http_server.start(0)
    tornado.ioloop.IOLoop.current().start()
