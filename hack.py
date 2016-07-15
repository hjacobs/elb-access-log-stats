#!/usr/bin/env python3

import collections
import math
import sys


def _percentile(N, percent, key=lambda x: x):
    """
    Find the percentile of a list of values.

    @parameter N - is a list of values. Note N MUST BE already sorted.
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of N.

    @return - the percentile of the values

    >>> percentile([0,1], 0.5)
    0.5

    >>> percentile([0,1,2], 0.9)
    1.8

    >>> percentile([], 0.9) is None
    True
    """

    if not N:
        return None
    k = (len(N) - 1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (c - k)
    d1 = key(N[int(c)]) * (k - f)
    return d0 + d1


latencies = collections.defaultdict(list)
request_sizes = collections.defaultdict(list)
response_sizes = collections.defaultdict(list)

with open(sys.argv[1]) as fd:
    for line in fd:
        parts = line.split(' ', 11)
        status_code = parts[7]
        http_method = parts[-1].split(' ', 1)[0].strip('"')
        latency = float(parts[4]) + float(parts[5]) + float(parts[6])
        latencies[(status_code, http_method)].append(latency)
        request_size = int(parts[9])
        request_sizes[(status_code, http_method)].append(request_size)
        response_size = int(parts[10])
        response_sizes[(status_code, http_method)].append(response_size)

for cont in (latencies, request_sizes, response_sizes):
    for key, values in sorted(cont.items()):
        print(key)
        values.sort()

        print(len(values))
        print(_percentile(values, 0.99))
        print(_percentile(values, 0.95))
        print(_percentile(values, 0.75))
        print(_percentile(values, 0.5))
