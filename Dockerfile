FROM python:3.8.13-slim-buster
RUN mkdir /app
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt

#Enable this line for GCP Cloud run
RUN nohup python -m SimpleHTTPServer 8080

CMD ["python", "file_explorer_plugin.py"]