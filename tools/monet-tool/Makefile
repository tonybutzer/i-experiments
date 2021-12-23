cat:
	cat Makefile

Image=tbutzer/monet-tool 
build:
	docker build -t ${Image} .


run:
	docker run -it ${Image} bash

monet-grab:
	echo Ride your pony, ride your pony
	echo Ride your pony come on, come on
	echo Mony Mony
	echo Feel all right, I said yeah, yeah, yeah, yeah, yeah
	cp -r ~/opt/monet/monet/ .
	cp ~/opt/monet/setup.py .
	cp ~/opt/monet/requirements.txt .


help:
	docker run -it ${Image} monet --help


siouxfalls:
	docker run -v /home/ec2-user/data:/home/monet/imagery -it ${Image} monet  43.49 -96.69  -c 25 -s 2020-01-01 -e 2020-12-31 -t -D --radius 10000
test-jpg:
	docker run -v /home/ec2-user/data:/home/monet/imagery -it ${Image} monet -22.59 -44.03  -c 25 -s 2020-01-01 -e 2020-12-31 -t 


echo:
	echo https://smartgitlab.com/infrastructure/monet

