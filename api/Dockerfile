FROM python:3.10-slim-buster

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt 

COPY . /app/
EXPOSE 8000
ENTRYPOINT [ "uvicorn" ]
CMD [ "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" ]