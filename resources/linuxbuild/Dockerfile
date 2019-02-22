# Ubuntu 16.04 LTS 
FROM python

RUN apt-get update && \
  apt-get upgrade -y && \
  apt-get install -y sudo && \
  apt-get install -y vim && \
  apt-get install -y  software-properties-common && \
  add-apt-repository ppa:webupd8team/java -y && \
  apt-get update && \
  echo oracle-java7-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections && \
  apt-get install -y oracle-java8-installer --allow-unauthenticated && \
  apt-get clean

# create a root user
RUN adduser --disabled-login --gecos "" user
RUN adduser user sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers


ADD . /home/user/reputation

# make user own the reputation folder
RUN chown -R user:user /home/user/reputation

# color PS1
RUN mv /home/user/reputation/resources/linuxbuild/.bashrc /home/user/ && \
	cat /home/user/.bashrc >> /etc/bash.bashrc

# Install python dependencies
RUN bash /home/user/reputation/scripts/install

WORKDIR /home/user/reputation	
USER user


CMD ["/bin/bash"]



