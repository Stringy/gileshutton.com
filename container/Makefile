
.PHONY: build
build:
	docker build --platform=linux/amd64 -t gileshutton.com:latest -f Dockerfile ..

.PHONY: save
save:
	docker save -o website.tar gileshutton.com:latest
	gzip -f website.tar

.PHONY: upload
upload: save
	scp website.tar.gz website:~/

.PHONY: load
load: upload
	ssh website -- "gunzip -f website.tar.gz && docker load -i website.tar"

.PHONY: build-and-deploy
build-and-deploy: build load
	ssh website -- "docker stop gileshutton.com || true"
	ssh website -- docker run -d --rm -v /etc/letsencrypt/:/certs:ro -p 80:80 -p 443:443 --name gileshutton.com gileshutton.com:latest
