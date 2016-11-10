"""
Decorator for method call statistics (count and runtime)

Usage:
    >>> @call_stats
        def f1():
            pass
    >>> @call_stats
        def f2():
            pass
    >>> f1()
    >>> f1()
    >>> f2()
    >>> f1.call_stats
    ['f1', 2, 3.0994415283203125e-06]
    >>> add.print_call_stats()
    f1() called 2 times. Total runtime 3.10e-06s (1.55e-06s per call)
    >>> call_stats.print_all_call_stats()
    f1() called 2 times. Total runtime 3.10e-06s (1.55e-06s per call)
    f2() called 1 times. Total runtime 1.43e-06s (1.43e-06s per call)


Author:
    Name: Johannes Engell Kamber
    Last edited: 2016-10-30
    Licence: See licence.txt
"""

from functools import update_wrapper
from time import time
from collections import deque
import numpy as np

class call_stats():
    """
    Decorator. Saves the the number of times a function is called along with the total processing time

    Example:
        >>> @call_stats
            def f1():
                pass
        >>> @call_stats
            def f2():
                pass
        >>> f1()
        >>> f1()
        >>> f2()
        >>> f1.call_stats
        ['f1', 2, 3.0994415283203125e-06]
        >>> f1.print_call_stats()
        f1() called 2 times. Total runtime 3.10e-06s (1.55e-06s per call)
        >>> call_stats.print_all_call_stats()
        f1() called 2 times. Total runtime 3.10e-06s (1.55e-06s per call)
        f2() called 1 times. Total runtime 1.43e-06s (1.43e-06s per call)
    """

    _instances = {}

    def __init__(self, func):
        update_wrapper(self, func)  # Updates the meta variables
        self._func = func
        self._call_count = 0
        self._n_call_stat_hist = 1000
        self._call_hist = deque(maxlen=self._n_call_stat_hist)
        call_stats._instances[func] = self

    def __call__(self, *args, **kwargs):
        t1 = time()
        resp = self._func(*args, **kwargs)
        t2 = time()
        self._call_hist.append(t2-t1)
        self._call_count += 1

        return resp

    @property
    def call_stats(self):
        """
        Property call_stats (read only).

        Returns the call stats for a given function in the format ['function_name', call_count, call_history]
        """
        return [self.__name__, self._call_count, np.sum(self._call_hist),
                np.mean(self._call_hist), np.std(self._call_hist)]

    @call_stats.setter
    def call_stats(self, value):
        raise AttributeError('The call_stats property is read only')

    @property
    def n_call_stat_hist(self):
        return self._n_call_stat_hist

    @n_call_stat_hist.setter
    def n_call_stat_hist(self, value):
        self._n_call_stat_hist = value
        self._call_hist = deque(maxlen=self.n_call_stat_hist)

    def print_call_stats(self):
        """Prints the method call statistics of the function"""
        name, count, tot, mean, std = self.call_stats
        if count is 0:
            print("%s() called 0 times" % name)
            return None
        print('%s() called %i times. Total %.2es, mean %.2es, std %.2es' %
              (name, count, tot, mean, std))
        return None

    @staticmethod
    def print_all_call_stats():
        """Prints the method call statistics of all decorated functions"""
        stats = []
        for func, deco in call_stats._instances.items():
            stats.append((deco, deco.call_stats[1],))
        stats.sort(key=lambda tup: tup[1], reverse=True)
        overflow = False
        for deco, count in stats:
            deco.print_call_stats()
            if count > deco.n_call_stat_hist:
                overflow = True
        if overflow:
            print('NB: Some statistics are calculated using truncated call history')
        return None

# Examples
if __name__ == "__main__":

    @call_stats
    def add(a, b):
        """DocString for add()"""
        return a+b

    @call_stats
    def fib(n):
        if n <= 1:
            return n
        t = fib(n-1) + fib(n-2)
        return t

    add.n_call_stat_hist = 10000
    fib.n_call_stat_hist = 10000

    from random import randint

    for i in range(0,6):
        add(randint(5, 10), randint(500, 1000))
    fib(5)

    call_stats.print_all_call_stats()
