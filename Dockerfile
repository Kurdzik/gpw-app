FROM ubuntu:22.04

RUN apt update && apt upgrade -y
RUN apt install python3 -y
RUN apt install python3-pip -y
RUN apt install nano

COPY . .

RUN pip3 install -r build/requirements.txt

ENV DB_CONN_STRING=postgresql://j341:ED1F_a359b0@psql01.mikr.us:5432/db_j341

EXPOSE 5000

CMD ["flask","run","--host","0.0.0.0","--port","5000"]