FROM python:3

WORKDIR ./

COPY requirements.txt ./
RUN pip install -r requirements.txt

EXPOSE 5000

CMD [ "python", "version.py"]

COPY . .