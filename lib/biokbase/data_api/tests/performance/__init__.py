import datetime

class WallClockTimer(object):
    def __enter__(self):
        self.start = datetime.datetime.utcnow()
        return self
    
    def __exit__(self, *args):
        self.end = datetime.datetime.utcnow()
        self.elapsed = self.end - self.start