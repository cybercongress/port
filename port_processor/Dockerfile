FROM python:3.8

ADD requirements.txt /
RUN pip install -r ./requirements.txt

ADD cyber.py /
ADD config.py /
ADD db.py /
ADD db_subscription.py /
ADD eth.py /
ADD main.py /
ADD processor.py /
ADD exceptions_decorators.py /

CMD python -u ./main.py --log=INFO