# syntax=docker/dockerfile:1
FROM --platform=linux/amd64 python:3

WORKDIR /image-processor

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5001

CMD [ "python3", "-u", "-m" , "flask", "run", "--host=0.0.0.0","--port=5001" ,"--debug"]