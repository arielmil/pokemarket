FROM ubuntu:latest

RUN apt-get update && apt-get install -y cron postgresql-client

# Add crontab file in the cron directory
ADD ./utils/cronFiles/crontab /etc/cron.d/crontest

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/crontest

RUN mkdir backup

# Run the command on container startup
RUN touch /home/crontestOutput
CMD cron && tail -f /home/crontestOutput
