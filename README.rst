=========================
ELB Access Log Statistics
=========================

** WORK IN PROGRESS **

* REST API to retrieve ELB access log statistics
* Download access log from S3
* Analyze and expose statistics:

  * Latencies by status code and HTTP method
  * Request/response sizes by status code and HTTP method

Building
========

.. code-block:: bash

    $ sudo pip3 install -U scm-source
    $ scm-source
    $ docker build -t elb-access-log-stats .

Running
=======

.. code-block:: bash

    $ # NOTE: you need to provide AWS credentials somehow (this is automagic on EC2)
    $ docker run -it -p 8080:8080 -e BUCKET=mybucket-123-eu-central-1 elb-access-log-stats
    $ # now open http://localhost:8080/ui/ in your browser to see the Swagger UI
