import argparse
import json
import logging
import tornado.web
import tornado.httpclient
import tornado.ioloop
import tornado.gen
import tornado.websocket
import tornado.locks
import settings
from watcher import JitterDog
import uuid

jitter_dog = JitterDog('/mnt/jitters')

change_events = tornado.locks.Event()
clients = []

class JenkinsHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        print("HITTTTTIN")
        location = self.get_argument('location',None)
        branch = self.get_argument("branch", None)
        print(branch, location)
        link = 'https://raw.githubusercontent.com/JitterTAP/jitter-bug/' + branch +  '/assets/css/main.css?thing=' + str(uuid.uuid4())
        print(link)
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield client.fetch(link)
        print(response.body)
        with open('/mnt/jittertap_' + location + '/jitter-bug/assets/css/main.css', 'wb') as f:
            f.write(response.body)
        for client in clients:
            msg = json.dumps({'changed': True})
            client.write_message(msg)

class HealthCheckHandler(tornado.web.RequestHandler): # noqa
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    @tornado.gen.coroutine
    def get(self):
        self.write('ok')


class JitterDogHandler(tornado.websocket.WebSocketHandler): # noqa
    def open(self):
        self.id = uuid.uuid4()
        print("Connected to Jitter Dog Socket %s!\n" % self.id)
        clients.append(self)

    @tornado.gen.coroutine
    def on_message(self, _):
        pass
        #while True:
        #    yield change_events.wait()
        #    result = yield jitter_dog.get_message(self.id)
        #    json_result = json.dumps(result)
        #    print(json_result)
        #    self.write_message(json_result)

    def check_origin(self, origin):
        return True

    def on_close(self):
        clients.remove(self)
        print("Closing Jitter Dog Socket\n")






def main():
    parser = argparse.ArgumentParser(description='Who let the dogs out?')
    parser.add_argument('--path', type=str)
    parser.add_argument('--region', type=int)
    args = parser.parse_args()
    ROUTES = [
    (r'/health', HealthCheckHandler),
    (r'/jitterdog', JitterDogHandler),
    (r'/jenkins', JenkinsHandler),
    (r'/(.+)', tornado.web.StaticFileHandler, {'path': args.path})
    ]
    APPLICATION = tornado.web.Application(ROUTES)
    if args.region is 1:
        APPLICATION.listen(15000)
    else:
        APPLICATION.listen(16000)
    jitter_dog.set_path(args.path)
    print("starting server") 
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
