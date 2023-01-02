FROM python:3.9
WORKDIR /TTA
COPY ./ ./
EXPOSE 4001
RUN pip install -r Requirements.txt