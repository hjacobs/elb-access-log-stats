#!/usr/bin/env python3

from gevent import monkey
monkey.patch_all()

import boto3
import collections
import connexion
import datetime
import logging
import os
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


def _round(f):
    # reduce precision on purpose for JSON
    return round(f, 8)


def read_files(s3, bucket, files):
    for log_file in files:
        response = s3.get_object(Bucket=bucket, Key=log_file)
        contents = response['Body'].read()
        for line in contents.rstrip().split(b'\n'):
            yield line


def get_stats(account_id: str, region: str, prefix: str):
    bucket = os.getenv('BUCKET')

    path = '{prefix}/AWSLogs/{account_id}/elasticloadbalancing/{region}/{date:%Y}/{date:%m}/{date:%d}/'.format(
            prefix=prefix, account_id=account_id, region=region, date=datetime.datetime.utcnow())

    s3 = boto3.client('s3')
    response = s3.list_objects(Bucket=bucket, Prefix=path, Delimiter='/')

    contents = response.get('Contents', [])

    most_recent = None
    for row in contents:
        if not most_recent or row['LastModified'] > most_recent['LastModified']:
            most_recent = row

    if not most_recent:
        return 'access log not found', 404

    # TODO: we need to find the most recent "complete" set of access logs
    # (each ELB instance writes its own log file, but not at the same time)
    files = []
    common_prefix = most_recent['Key'].rsplit('Z_', 1)[0]
    for row in contents:
        if row['Key'].startswith(common_prefix):
            files.append(row['Key'])

    latencies = collections.defaultdict(list)
    request_sizes = collections.defaultdict(list)
    response_sizes = collections.defaultdict(list)

    for line in read_files(s3, bucket, files):
        parts = line.split(b' ', 11)
        status_code = parts[7].decode('ascii')
        http_method = parts[-1].split(b' ', 1)[0].strip(b'"').decode('ascii')
        latency = float(parts[4]) + float(parts[5]) + float(parts[6])
        latencies[(status_code, http_method)].append(latency)
        latencies[(status_code, '*')].append(latency)
        request_size = int(parts[9])
        request_sizes[(status_code, http_method)].append(request_size)
        request_sizes[(status_code, '*')].append(request_size)
        response_size = int(parts[10])
        response_sizes[(status_code, http_method)].append(response_size)
        response_sizes[(status_code, '*')].append(response_size)

    dicts = {'latencies': latencies, 'request_sizes': request_sizes, 'response_sizes': response_sizes}
    result = {'_files': files}
    for name, cont in dicts.items():
        stats = {}
        for key, values in cont.items():
            status_code, http_method = key

            if status_code not in stats:
                stats[status_code] = {}

            if http_method not in stats[status_code]:
                stats[status_code][http_method] = {}

            values.sort()

            stats[status_code][http_method]['count'] = len(values)
            stats[status_code][http_method]['mean'] = _round(sum(values) / len(values))
            for p in (0.99, 0.95, 0.75, 0.5):
                stats[status_code][http_method]['p{}'.format(int(p*100))] = _round(_percentile(values, p))
        result[name] = stats
    return result


logging.basicConfig(level=logging.INFO)
app = connexion.App(__name__)
app.add_api('swagger.yaml')

if __name__ == '__main__':
    if not os.getenv('BUCKET'):
        print('Configuration error: BUCKET environment variable is not set')
        sys.exit(2)

    # run our standalone gevent server
    app.run(port=8080, server='gevent')
