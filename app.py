from tornado.web import Application,RequestHandler
from tornado.ioloop import IOLoop
from pymongo import MongoClient
from tornado.options import define, options
import json

define('port', default=8888, help='the port server is running on')


class NonIdHandler(RequestHandler):
    def initialize(self):
        self.set_header('Content-Type', 'application/json')

    def get(self):
        db = self.settings['db']
        collection = db['user']
        users = str(list(db.user.find()))
        self.write(users)
    def post(self):
        db = self.settings['db']
        collection = db['user']
        user_d = db.user.find().sort([("id", -1)]).next()
        # print(user_d)
        id = user_d['id']+1
        data = json.loads(self.request.body)
        user_data = {
            "id": int(id),
            "fName": data['fName'],
            "lName": data['lName']
        }
        db.user.insert(user_data)
        self.write(f"Successfully inserted user data\n{user_data}")

class IdHandler(RequestHandler):
    def initialize(self):
        self.set_header('Content-Type', 'application/json')

    def get(self, id):
        db = self.settings['db']
        collection = db['user']
        user_d = db.user.find({"id": int(id)})
        user_data = None
        for d in user_d:
            user_data = d
        # print(user_data)
        if user_data==None:
            self.write(f"User with {id} not found in the database")
        # print(list(user_data))
        else:
            self.write(str(user_data))

    def put(self, id):
        db = self.settings['db']
        collection = db['user']
        user_d = db.user.find({"id": int(id)})
        user_data = None
        for d in user_d:
            user_data = d
        if user_data==None:
            self.write(f"User with {id} not found in the database")
        else:
            data = json.loads(self.request.body)
            user_data = {
                "id": int(id),
                "fName": data['fName'],
                "lName": data['lName']
            }
            db.user.update({"id": int(id)}, user_data)
            self.write(f"Successfully updated the user {id}\n{user_data}")

    def delete(self, id):
        db = self.settings['db']
        collection = db['user']
        user_d = db.user.find({"id": int(id)})
        user_data = None
        for d in user_d:
            user_data = d
        if user_data==None:
            self.write(f"User with {id} not found in the database")
        else:
        # user_data = db.user.find_one({"id": double(id)})
            db.user.remove({"id": int(id)})
            self.write(f"Successfully deleted the user {id}\n{str(user_data)}")


if __name__=='__main__':
    cursor = MongoClient('mongodb://localhost:27017')
    application = Application([
        (r"/users", NonIdHandler),
        (r"/users/([0-9]+)", IdHandler),
    ], db = cursor['test'])

    application.listen(options.port)
    print("Listening on port {}".format(options.port))
    IOLoop.current().start()
