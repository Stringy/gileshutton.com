PHONY: deploy
deploy:
	make -C container build-and-deploy

PHONY: debug
debug:
	hugo serve -D
