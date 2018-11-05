server_version=6.3.4

base_image=seafileltd/base:pi
base_image_squashed=seafileltd/base:pi-squashed
server_image=seafileltd/seafile:$(server_version)-pi
server_image_squashed=seafileltd/seafile:$(server_version)-pi-squashed
latest_server_image=seafileltd/seafile:pi

all:
	@echo
	@echo Please use '"make base"' or '"make server"' or '"make push"'.
	@echo

base:
	docker pull phusion/baseimage:0.11
	cd base && docker build -t $(base_image) .

server:
	cd seafile && cp -rf ../../scripts ./ && docker build -t $(server_image) .
	docker tag $(server_image) $(latest_server_image)

push-server:
	docker push $(server_image)
	docker push $(latest_server_image)

push: push-base push-server

.PHONY: base server push push-base push-server
