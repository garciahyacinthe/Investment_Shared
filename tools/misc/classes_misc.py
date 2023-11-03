
def iterable(cls):
    def iterfn(self):
        iters = dict((x,y) for x,y in cls.__dict__.items() if x[:2] != '__')
        iters.update(self.__dict__)

        for x,y in iters.items():
            yield x,y

    cls.__iter__ = iterfn
    return cls