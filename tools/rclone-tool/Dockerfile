FROM ubuntu
# /caldera/projects/usgs/eros/usmart

WORKDIR /home/ubuntu

RUN groupadd -r -g 1000 ubuntu && useradd -r -u 1000 -g ubuntu ubuntu \ 
	&& apt-get update \
	&& apt-get install openssh-server -y \
	&& apt-get install rclone -y 

COPY rclone.conf /home/ubuntu/.rclone.conf

USER ubuntu
