from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from tornado.queues import Queue
from tornado import gen, locks


class JitterDog(FileSystemEventHandler):

    def __init__(self, path):
        self.path = path
        self._observer = Observer()
        self._lock = locks.Lock()
        self._queues = {}

    @gen.coroutine
    def add_listener(self, ident):
        with (yield self._lock.acquire()):
            self._queues[ident] = Queue()

    @gen.coroutine
    def remove_listener(self, ident):
        with (yield self._lock.acquire()):
            del self._queues[ident]

    def get_message(self, ident):
        return self._queues[ident].get()

    @gen.coroutine
    def put_message(self, event):
        event_dict = {
            'event_name': event.event_type,
            'src_path': event.src_path,
            'is_directory': event.is_directory,
        }
        if not event.is_directory:
            for key, queue in self._queues.items():
                yield queue.put(event_dict)

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

    def set_path(self,path):
        self.path = path
