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

test-jpg:
	docker run -v /home/ec2-user/data:/home/monet/imagery -it ${Image} monet -22.59 -44.03  -c 25 -s 2020-01-01 -e 2020-12-31 -t
