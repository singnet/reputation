# Ubuntu 16.04 LTS 
FROM python

# create a non-root user
RUN adduser --disabled-login --gecos "" user

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



