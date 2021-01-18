from tornado.web import RequestHandler, Application, HTTPError
from tornado.gen import coroutine
from tornado.ioloop import IOLoop
from tornado.options import define, options
import motor
from motor import motor_tornado
from bson.json_util import dumps, loads



define('port', default=8888, help='A port the server is running on...', type=int)

class MainHandler(RequestHandler):
    def initialize(self):
        self.set_header('Content-Type', 'application/json')
        self.db=self.settings['db']
        self.collection = self.db['user']

    @coroutine
    def get(self):
        self.write('<h1>User List</h1>')
        self.write('<ul>')
        users = self.collection.find() #.each(self._got_data)
        while(yield users.fetch_next):
            user = users.next_object()
            self.write('<li>{}</li>'.format(dumps(user)))
        self.write('</ul>')
        self.finish()
    # def _got_data(self, data, error):
    #     if error:
    #         raise HTTPError(500, error)
    #     elif data:
    #         self.write(f'<li>{data}</li>')
    #     else:
    #         self.write('</ul>')
    #         self.finish()
    @coroutine
    def post(self):
        users = self.collection.find().sort([("id", -1)])
        while(yield users.fetch_next):
            user = users.next_object()
            break
        id = user['id']+1
        data = loads(self.request.body)
        print(data)
        user_data = {
            "id": int(id),
            "fName": data['fName'],
            "lName": data['lName']
        }
        self.collection.insert_one(user_data)
        self.write(f"Successfully inserted user data\n{user_data}")



if __name__=='__main__':
    cursor = motor.MotorClient('mongodb://localhost:27017')
    application = Application([
        (r"/", MainHandler),
        # (r"/users/([0-9]+)", IdHandler),
    ], db = cursor['test'])

    application.listen(options.port)
    print("Listening on port {}".format(options.port))
    IOLoop.current().start()
