FROM golang
RUN apt-get update \
  && apt-get install -y postgresql postgresql-contrib \
  && apt-get install sudo \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
  &&  /etc/init.d/postgresql start \
  && sudo -u postgres -i psql -c "ALTER USER postgres PASSWORD 'postgres';" -U postgres \   
  && sudo -u postgres -i psql -c 'drop database if exists "postgres";' -U postgres \
  && sudo -u postgres -i psql -c 'create database "postgres" OWNER postgres;' -U postgres \
  && sudo -u postgres -i psql -c 'create database "postgres" OWNER postgres;' -U postgres


