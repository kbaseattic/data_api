"""
Text progress bar
"""
import sys

class PBar(object):
    """Text progress bar.
    """
    c0 = '.' # left end marker
    c1 = '_' # completed char
    c2 = '|' # un-completed char
    c3 = '.' # right end marker
    p = ['|', '/', '-', '\\'] # cur-pos spinner chars

    def __init__(self, total, width, ostrm=sys.stdout):
        self.n, self.w, self.c, self.i = total, width, 0, 0
        self.o = ostrm

    def inc(self, count):
        self.c = min(self.c + count, self.n) # new cur pos.
        d = int(1.* self.c / self.n * self.w) # completed chars
        # uncompleted chars, with space for cur pos. char
        d, x = (self.w - 1, 0) if d == self.w else (d, self.w - d - 1)
        pct = int(round(100. * self.c / self.n)) # percent completed
        self.i = (self.i + 1) % len(self.p) # next cur-pos char.
        self.o.write('\r{}{}{}{}{} {:d}% ({}/{})'.format(
            self.c0, self.c1*d, self.p[self.i], self.c2*x, self.c3,
            pct, self.c, self.n)),
        self.o.flush()

    def done(self):
        self.c = self.n
        self.o.write('\r{}{}{} 100% ({}/{})\n'.format(
            self.c0, self.c1*self.w, self.c3, self.n, self.n))

# Demo
if __name__ == '__main__':
    import time
    # optional first arg. for count
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 123
    # optional second arg. for width
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    # create progress bar
    pbar = PBar(n, w)
    # do something that progresses
    step = n/50
    for i in xrange(0, n, step):
        pbar.inc(step)
        time.sleep(0.1)
    pbar.done()