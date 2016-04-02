import logging
import sys
import time
import unittest
from doekbase.data_api.util import MonitorMemory, get_logger, basic_config

_log = get_logger(__name__)

alerted = {}

MB = 1024 * 1024

def icanhaz_alert(mm, avail, thresh, name):
    assert avail < thresh
    alerted[name] = avail
    _log.debug('\nalerted: {:d} MB'.format(thresh / MB))

def memory_hog(name):
    _log.debug('run memory hog until alert {}'.format(name))
    a, i = [], 0
    while 1:
        a.append(['x'] * 1000000)
        if _log.isEnabledFor(logging.DEBUG):
            sys.stdout.write('{:12d} MB\r'.format(len(a)))
            sys.stdout.flush()
        if alerted.get(name, False):
            break
        # allow other threads in, once in a while
        i += 1
        if i == 100:
            i = 0
            time.sleep(0.1)

class MyTestCase(unittest.TestCase):
    def test_anyalert(self):
        """test that alerting for memory works at all"""
        num_mb = 1000000
        mm = MonitorMemory()
        # call 'alert' when memory goes below a really high amount
        mm.add_alert(num_mb, icanhaz_alert, 'key')
        # run in a thread
        mm.start()
        while 1:
            time.sleep(0.5)
            if alerted.get('key', False):
                break
        # print('stopping..')
        mm.stop()
        mm.join()
        # check that memory is at the right level
        self.assertLess(alerted['key'], num_mb * MB)
        # print('stopped. avail: {} MB'.format(alerted['key']/1024/1024))
        
    @unittest.skipIf(True, "skip memory test")
    def test_basic(self):
        """one memory alert"""
        num_mb = 10000
        mm = MonitorMemory()
        # call 'alert' when memory goes below 10GB
        mm.add_alert(num_mb, icanhaz_alert, 'key')
        # run in a thread
        mm.start()
        memory_hog('key')
        # print('stopping..')
        mm.stop()
        mm.join()
        # check that memory is at the right level
        self.assertLess(alerted['key'], num_mb * MB)
        # print('stopped. avail: {} MB'.format(alerted['key']/1024/1024))

    @unittest.skipIf(True, "skip memory test")
    def test_multi(self):
        """multiple memory alerts"""
        num_mb = [10000, 9000, 8000]
        mm = MonitorMemory()
        # add multiple alerts
        for mb in num_mb:
            _log.debug('add alert for {} MB'.format(mb))
            mm.add_alert(mb, icanhaz_alert, 'a{}'.format(mb))
        # run in a thread
        mm.start()
        min_key = 'a{}'.format(min(num_mb))
        memory_hog(min_key)
        _log.debug('stopping..')
        mm.stop()
        mm.join()
        # check that all alerts fired
        for mb in num_mb:
            self.assertIn('a{}'.format(mb), alerted, 'missing key')
        # check that memory is at the right level
        self.assertLess(alerted[min_key], min(num_mb) * MB)
        _log.debug('stopped. avail: {} MB'.format(alerted[min_key] / MB))

if __name__ == '__main__':
    # set DEBUG if number of '-v' options is 2 or more
    num_vb = sum([sum([1 if c == 'v' else 0 for c in list(opt)])
                  for opt in sys.argv if opt.startswith('-v')])
    if num_vb > 1:
        basic_config(logging.DEBUG)
        _log.setLevel(logging.DEBUG)
    # run
    unittest.main()
