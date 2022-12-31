FROM python:3.9

ADD ./ ./

EXPOSE 5432

RUN pip install -r Requirements.txt

CMD [ "python3","./main.py" ]