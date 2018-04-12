server_version=6.2.5

base_image=seafileltd/base:16.04
base_image_squashed=seafileltd/base:16.04-squashed
server_image=seafileltd/seafile:$(server_version)
latest_server_image=seafileltd/seafile:latest

all:
	@echo
	@echo Pleaes use '"make base"' or '"make server"' or '"make push"'.
	@echo

base:
	cd base && docker build -t $(base_image) .

squash-base:
	docker-squash --tag $(base_image_squashed) $(base_image) --from-layer phusion/baseimage:0.10.1
	docker tag $(base_image_squashed) $(base_image)

server:
	cd seafile && docker build -t $(server_image) .
	docker tag $(server_image) $(latest_server_image)

push-base:
	docker push $(base_image)

push-server:
	docker push $(server_image)
	docker push $(latest_server_image)

push: push-base push-server

.PHONY: base server push push-base push-server
