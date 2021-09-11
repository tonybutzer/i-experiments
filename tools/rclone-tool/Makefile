Image=tbutzer/rclone-tool

build:
	# docker build -t ${Image} --build-arg ssh_prv_key="$(cat ~/.ssh/id_rsa)" --build-arg ssh_pub_key="$(cat ~/.ssh/id_rsa.pub)" --squash .
	# docker build -t ${Image} --build-arg ssh_prv_key="$(cat ~/.ssh/id_rsa)" --build-arg ssh_pub_key="$(cat ~/.ssh/id_rsa.pub)" .
	docker build -t ${Image} .


run:
	docker run -it -v /home/ec2-user/.ssh:/home/ubuntu/.ssh ${Image} bash


test-ssh:
	ssh butzer@tallgrass.cr.usgs.gov


publish:
	(cd ../../; make publish)
