FROM ubuntu:22.04

RUN apt update && apt upgrade -y
RUN apt install python3 -y
RUN apt install python3-pip -y
RUN apt install nano

COPY . .

RUN python3 set_environmental_vars.py
RUN rm set_environmental_vars.py

RUN pip3 install -r requirements.txt

EXPOSE 5000

# ENTRYPOINT [ "bash" ]

CMD ["flask","run","--host","0.0.0.0","--port","5000"]