FROM python:3.8

ADD requirements.txt /
RUN pip install -r ./requirements.txt

ADD cyb.py /
ADD gol.py /
ADD main.py /
ADD config.py /

CMD python -u ./main.py