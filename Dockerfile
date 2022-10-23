FROM python:3.10

WORKDIR /home

ENV API_TOKEN=...
ENV QUIZLET_LINK=...
ENV QUIZLET_LOGIN=...
ENV QUIZLET_PASSWORD=...

WORKDIR /app

COPY . .

RUN pip3 install --no cache-dir -r requirements.txt

EXPOSE 5000

CMD ['python', 'main.py']
