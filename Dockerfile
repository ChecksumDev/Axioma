FROM python:3.10-alpine

# Install system packages
RUN apk add --no-cache ffmpeg

RUN adduser --disabled-password --gecos "" axioma
RUN chown -R axioma:axioma /home/axioma

USER axioma

COPY . /home/axioma/
WORKDIR /home/axioma/

RUN pip install -r requirements.txt --no-cache-dir

CMD ["python", "src/main.py"]
