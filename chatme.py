#coding:utf-8
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options# self-define command line module
import hashlib
import xmltodict
import time
tornado.options.define("port",type=int,default=8000,help="define port")
    #self-define port by command line
WECHAT_TOKEN = 'xiyi'
class IndexHandler(tornado.web.RequestHandler):

    def get(self):
       self.write("Hello,Mars!")
class WechatHandler(tornado.web.RequestHandler):
    def get(self):
        signature = self.get_argument('signature')
        timestamp = self.get_argument('timestamp')
        nonce = self.get_argument('nonce')
        echostr = self.get_argument('echostr')
        temp = [WECHAT_TOKEN,timestamp,nonce]
        temp.sort()
        temp_str = ''.join(temp)
        temp_str = hashlib.sha1(temp_str).hexdigest()
        if (temp_str ==signature):
            self.write(echostr)
        else:
            self.send_error(403)

    def post(self):
        xml_data = self.request.body
        xml_str = xmltodict.parse(xml_data)
        to = xml_str['xml']['ToUserName']
        come = xml_str['xml']['FromUserName']
        msg_type = xml_str['xml']['MsgType']
        content = xml_str['xml']['Content']
        if 'text' == msg_type:
            dict_data = {'xml':
                    {
                        'ToUserName':come,
                        'FromUserName':to,
                        'CreateTime':time.time(),
                        'MsgType':'text',
                        'Content':content,


                        }}
            
        else:
             dict_data = {'xml':
                                                      
                     {'ToUserName':come,
                      'FromUserName':to,
                    'CreateTime':time.time(),
                     'MsgType':'text',
                    'Content':"Bad request,error"
                    }}
        
        resp_xml = xmltodict.unparse(dict_data)
        self.write(resp_xml)

class Access_token(object):
    # get the wechat API access token
    
    _access_token = {
            "data":"",
            "updatetime":datetime.datetime.now()
            }
    @tornado.gen.coroutine
    @classmethod
    def update_access_token(cls):
        client = AsyncHTTPClient()
            #create a async client
        url ="https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (WECHAT_APPID, WECHAT_APPSECRET)
        resp =yield client.fetch(url)
            #the writing way of GET request method
        #req = HTTPReqest(url,method="post",)
        #resp = yield client.fetch(req)
            #the writing way of POST request method
        dict_data = {
                "name":name,
                "type":event,
                "appid":appid
                }
        json_data = json.dumps(dict_data)
        #when call the yield method,turn back value can't be use return,but use raise tornado.gen.Return
        raise tornado.gen.Return(json_data)
        
class QRCodeHandler(RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        access_token = yield AccessToken.get_access_token()
        url = 
        scend_id = self.get_argument("scend_id")
        req_body ='{"expire_seconds":7200,"action_info":{"scene_id":%s}}}'
        client =AsyncHTTPClient()
        req = HTTPRequest(url,method="POST",body=req_body)
        resp = yield client.fetch(req)
        if "errcode" in resp.body:
            self.write("error")
        else:
            resp_data =json.loads(resp.body)
            ticket = resp_data["ticket"]
            self.write('<img src="http://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s"./>'%ticket)

if __name__ == '__main__':
    #parse self-define options
    tornado.options.parse_command_line()
    setting = {
            debug:True,
            static_path:"".join(os.path.dir(__files__),"static"),
            }
    app = tornado.web.Application([(r'/',IndexHandler),
        (r'/wechat8011',WechatHandler),
        (r'/wechat8011/qrcode',QRCodeHandler,
        ],
        **settings)
    #app.listen(8000)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(tornado.options.options.port)
    #http_server.bind(8000)
    #http_server.start(0)
    tornado.ioloop.IOLoop.current().start()
