server_version=6.2.10

base_image=seafileltd/base:16.04
base_image_squashed=seafileltd/base:16.04-squashed
pro_base_image=seafileltd/pro-base:16.04
pro_base_image_squashed=seafileltd/pro-base:16.04-squashed
server_image=seafileltd/seafile:$(server_version)
pro_server_image=docker-internal.seadrive.org/seafileltd/pro-seafile:$(server_version)
pro_server_image_squashed=docker-internal.seadrive.org/seafileltd/pro-seafile:$(server_version)-squashed
latest_server_image=docker-internal.seadrive.org/seafileltd/pro-seafile:latest

all:
	@echo
	@echo Pleaes use '"make base"' or '"make server"' or '"make push"'.
	@echo

base:
	docker pull phusion/baseimage:0.9.19
	docker-squash --tag phusion/baseimage:latest phusion/baseimage:0.9.19
	docker tag phusion/baseimage:latest phusion/baseimage:0.9.19
	cd base && docker build -t $(base_image) .
	docker-squash --tag $(base_image_squashed) $(base_image)
	docker tag $(base_image_squashed) $(base_image)

pro-base:
	cd pro_base && docker build -t $(pro_base_image) .
	docker-squash --tag $(pro_base_image_squashed) $(pro_base_image)
	docker tag $(pro_base_image_squashed) $(pro_base_image)

pro-server:
	cd pro_seafile && docker build -t $(pro_server_image) .
	docker-squash --tag $(pro_server_image_squashed) $(pro_server_image) --from-layer=$(pro_base_image)
	docker tag $(pro_server_image_squashed) $(pro_server_image)
	docker tag $(pro_server_image) $(latest_server_image)

push-base:
	docker push $(base_image)

push-server:
	docker push $(server_image)

push-pro-server:
	docker push $(pro_server_image)
	docker push $(latest_server_image)

push: push-base push-server

.PHONY: base server push push-base push-server
