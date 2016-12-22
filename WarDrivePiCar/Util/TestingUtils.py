from threading import Thread


class TestThread(Thread):
    __thread_obj = None

    def __init__(self, thread_obj):
        Thread.__init__(self)
        Thread.name = "Unit-Testing separate thread"
        self.__thread_obj = thread_obj

    def run(self):
        self.__thread_obj.start()