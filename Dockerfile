FROM registry.opensource.zalan.do/stups/python:3.5.1-23

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY app.py /
COPY swagger.yaml /
COPY scm-source.json /

CMD /app.py
