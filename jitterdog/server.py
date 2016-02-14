import argparse
import json
import logging
import tornado.web
import tornado.ioloop
import tornado.gen
import tornado.websocket
import tornado.locks
import settings
from watcher import JitterDog
import uuid

jitter_dog = JitterDog('/mnt/jitters')

change_events = tornado.locks.Event()


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
        jitter_dog.add_listener(self.id)

    @tornado.gen.coroutine
    # _ = DATA
    def on_message(self, _):
        while True:
            result = yield jitter_dog.get_message(self.id)
            json_result = json.dumps(result)
            print(json_result)
            self.write_message(json_result)

    def check_origin(self, origin):
        return True

    def on_close(self):
        jitter_dog.remove_listener(self.id)
        print("Closing Jitter Dog Socket\n")




ROUTES = [
    (r'/health', HealthCheckHandler),
    (r'/jitterdog', JitterDogHandler)
]


APPLICATION = tornado.web.Application(ROUTES)


def main():
    parser = argparse.ArgumentParser(description='Who let the dogs out?')
    args = parser.parse_args()

    APPLICATION.listen(settings.PORT)
    logging.info('Serving on port: %d', settings.PORT)

    jitter_dog.start()
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
