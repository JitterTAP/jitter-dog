from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from tornado.queues import Queue
from tornado import gen


class JitterDog(FileSystemEventHandler):

    def __init__(self, path):
        self.path = path
        self._observer = Observer()
        self._queue = Queue()

    def get_message(self):
        return self._queue.get()

    @gen.coroutine
    def put_message(self, event):
        event_dict = {
            'event_name': event.event_type,
            'src_path': event.src_path,
            'is_directory': event.is_directory,
        }
        yield self._queue.put(event_dict)

    def start(self):
        self._observer.schedule(self, self.path, recursive=True)
        self._observer.start()

    def on_moved(self, event):
        self.put_message(event)

    def on_created(self, event):
        self.put_message(event)

    def on_deleted(self, event):
        self.put_message(event)

    def on_modified(self, event):
        self.put_message(event)
