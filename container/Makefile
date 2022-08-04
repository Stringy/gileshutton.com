
.PHONY: build
build:
	docker build -t gileshutton.com:latest -f Dockerfile ..

.PHONY: save
save:
	docker save -o website.tar gileshutton.com:latest

.PHONY: upload
upload: save
	scp website.tar website:~/

.PHONY: deploy
deploy: build upload
	ssh website -- docker load -i website.tar
