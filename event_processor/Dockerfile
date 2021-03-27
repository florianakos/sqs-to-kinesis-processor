FROM python:3

WORKDIR /usr/src/app/event_processor

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH="/usr/src/app/event_processor"

CMD [ "python", "./main.py" ]
