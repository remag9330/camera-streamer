import threading
# import inspect

class Mutex:
    def __init__(self, intial_value=None):
        self._value = intial_value
        self._lock = threading.Lock()

    def acquire(self):
        return Mutex.LockGuard(self)

    class LockGuard:
        def __init__(self, mutex):
            self.mutex = mutex

        @property
        def value(self):
            return self.mutex._value

        @value.setter
        def value(self, value):
            self.mutex._value = value
        
        def __enter__(self):
            # curframe = inspect.currentframe()
            # calframe = inspect.getouterframes(curframe, 2)
            # caller = calframe[1][3]

            # print(threading.current_thread().ident, "- Entering lock -", caller)
            self.mutex._lock.acquire()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            # curframe = inspect.currentframe()
            # calframe = inspect.getouterframes(curframe, 2)
            # caller = calframe[1][3]

            self.mutex._lock.release()
            # print(threading.current_thread().ident, "- Exiting lock -", caller)
