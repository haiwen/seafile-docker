server_version=6.2.10

base_image=seafileltd/base:16.04
pro_base_image=seafileltd/pro-base:16.04
base_image_squashed=seafileltd/base:16.04-squashed
server_image=seafileltd/seafile:$(server_version)
pro_server_image=seafileltd/pro-seafile:$(server_version)

all:
	@echo
	@echo Pleaes use '"make base"' or '"make server"' or '"make push"'.
	@echo

base:
	cd base && docker build -t $(base_image) .

pro-base:
	cd pro_base && docker build -t $(pro_base_image) .

squash-base:
	docker-squash --tag $(base_image_squashed) $(base_image) --from-layer phusion/baseimage:0.9.19
	docker tag $(base_image_squashed) $(base_image)

server:
	cd seafile && docker build -t $(server_image) .

pro-server:
	cd pro_seafile && docker build -t $(pro_server_image) .

push-base:
	docker push $(base_image)

push-server:
	docker push $(server_image)

push: push-base push-server

.PHONY: base server push push-base push-server
