
cat:
	cat Makefile
jup-run:
	docker run -it -p 8888:8888 -v `pwd`:/home/opt/ tbutzer/stac-notebook jupyter notebook --allow-root --ip="0.0.0.0" --NotebookApp.token='yaml'

publish:
	./gitpush.sh
