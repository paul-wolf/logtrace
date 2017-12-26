# -*- coding: utf-8 -*-
import uuid
import unittest
from . import LogTrace
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
s = [98, 127, 133, 147, 170, 197, 201, 211, 255]


class TestLogTrace(unittest.TestCase):

    def test_logtrace(self):
        trace = LogTrace(logger, level=logging.INFO)
        trace.add("first message")
        trace.add("second message")
        print(trace.emit_string())
        trace.emit("finally")
                
    def test_logtrace_unique_id(self):
        trace = LogTrace(logger=logger, unique_id=True, level=logging.INFO)
        trace.add("first message")
        trace.add("second message")
        print(trace.emit_string())

    def test_function(self):
        trace = LogTrace(logger=logger, level=logging.INFO)
        standard_deviation(s, trace=trace)
        print(trace.emit_string())
        
    def test_function_tag(self):
        trace = LogTrace(logger=logger, tag='STDDEV', level=logging.INFO)
        standard_deviation(s, trace=trace)
        print(trace.emit_string())
        
    def test_logtrace(self):
        trace = LogTrace(logger, unique_id=True, level=logging.INFO)
        trace.add("first message")
        trace.add("second message")
        print(trace.get_uid())
        trace.set_uid(uuid.uuid4())
        trace.set_uid(str(uuid.uuid4())) # could be a string
        trace.emit("finally")
        
def standard_deviation(lst, population=True, trace=None):
    """Calculates the standard deviation for a list of numbers.

    Just for testing LogTrace().

    """
    
    num_items = len(lst)
    trace.add('num_items={}'.format(num_items))
    
    mean = sum(lst) / num_items
    trace.add('mean={}'.format(mean))
    
    differences = [x - mean for x in lst]
    sq_differences = [d ** 2 for d in differences]
    ssd = sum(sq_differences)
    trace.add('ssd={}'.format(ssd))

    trace.add('population={}'.format(population))
    if population:
        variance = ssd / num_items
        trace.add('variance={}'.format(variance))
        return variance
    else:
        variance = ssd / (num_items - 1)
        sd = sqrt(variance)
        trace.add('sd={}'.format(sd))
        
    return sd 
        
if __name__ == '__main__':
    unittest.main()
