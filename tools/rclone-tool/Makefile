Image=tbutzer/rclone-tool

build:
	docker build -t ${Image} .


run:
	docker run -it ${Image} bash



publish:
	(cd ../../; make publish)
