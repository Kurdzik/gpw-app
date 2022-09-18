FROM ubuntu:22.04

RUN apt update && apt upgrade -y
RUN apt install python3 -y
RUN apt install python3-pip -y
RUN apt install nano

COPY . .

RUN pip3 install -r build/requirements.txt

# Database conn string
ENV DB_CONN_STRING=postgresql://j341:ED1F_a359b0@psql01.mikr.us:5432/db_j341

# Install cron
RUN apt-get update
RUN apt-get -y install cron

# Add execution rights to a script
# RUN chmod 0644 /root/gpw-app/daily_updates.sh

# RUN crontab -l | { cat; echo "00 23 * * * sh /root/gpw-app/daily_updates.sh"; } | crontab -

# Add execution rights to a TEST script
RUN chmod 0644 /root/gpw-app/test_script.sh

RUN crontab -l | { cat; echo "* * * * * sh /root/gpw-app/test_script.sh"; } | crontab -

EXPOSE 5000

CMD ["flask","run","--host","0.0.0.0","--port","5000"]