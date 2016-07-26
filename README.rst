=========================
ELB Access Log Statistics
=========================

** WORK IN PROGRESS **

* REST API to retrieve ELB access log statistics
* Download access log from S3
* Analyze and expose statistics:

  * Latencies by status code and HTTP method
  * Request/response sizes

.. code-block:: bash

    $ sudo pip3 install -U scm-source
    $ scm-source
    $ docker build -t elb-access-log-stats .
