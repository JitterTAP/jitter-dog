import argparse
import json
import logging
import tornado.web
import tornado.ioloop
import tornado.gen
import tornado.websocket
import tornado.locks
from jitterdog import settings
from jitterdog.watcher import JitterDog

jitter_dog = JitterDog('./')

change_events = tornado.locks.Event()


class HealthCheckHandler(tornado.web.RequestHandler): # noqa
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    @tornado.gen.coroutine
    def get(self):
        self.write('ok')


class JitterDogHandler(tornado.websocket.WebSocketHandler): # noqa
    def open(self):
        print("Connected to Jitter Dog Socket!\n")

    @tornado.gen.coroutine
    def on_message(self, _):
        while True:
            result = yield jitter_dog.get_message()
            json_result = json.dumps(result)
            print(json_result)
            self.write_message(json_result)

    def check_origin(self, origin):
        return True

    def on_close(self):
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