server_version=6.3.7

base_image=seafileltd/cluster-base:16.04
base_image_squashed=seafileltd/cluster-base:16.04-squashed
pro_base_image=seafileltd/cluster-pro-base:16.04
pro_base_image_squashed=seafileltd/cluster-pro-base:16.04-squashed
server_image=seafileltd/seafile:$(server_version)
server_image_squashed=seafileltd/seafile:$(server_version)-squashed
pro_server_image=seafileltd/cluster-seafile-pro:$(server_version)
pro_server_image_squashed=seafileltd/cluster-seafile-pro:$(server_version)-squashed
latest_pro_server_image=seafileltd/cluster-seafile-pro:latest
latest_server_image=seafileltd/seafile:latest

all:
	@echo
	@echo Pleaes use '"make base"' or '"make server"' or '"make push"'.
	@echo

base:
	docker pull phusion/baseimage:0.11
	docker-squash --tag phusion/baseimage:latest phusion/baseimage:0.11
	docker tag phusion/baseimage:latest phusion/baseimage:0.11
	cd base && docker build -t $(base_image) .
	docker-squash --tag $(base_image_squashed) $(base_image)
	docker tag $(base_image_squashed) $(base_image)
	docker rmi `docker images --filter "dangling=true" -q --no-trunc`

pro-base:
	cd pro_base && docker build -t $(pro_base_image) .
	docker-squash --tag $(pro_base_image_squashed) $(pro_base_image)
	docker tag $(pro_base_image_squashed) $(pro_base_image)
	docker rmi `docker images --filter "dangling=true" -q --no-trunc`

pro-server:
	cd pro_seafile && cp -rf ../../../templates ./ && cp -rf ../../scripts ./ && docker build -t $(pro_server_image) .
	docker-squash --tag $(pro_server_image_squashed) $(pro_server_image) --from-layer=$(pro_base_image)
	docker tag $(pro_server_image_squashed) $(pro_server_image)
	docker tag $(pro_server_image) $(latest_pro_server_image)
	docker rmi `docker images --filter "dangling=true" -q --no-trunc`

push-base:
	docker push $(base_image)

push-pro-base:
	docker tag $(pro_base_image) ${host}/$(pro_base_image)
	docker push ${host}/$(pro_base_image)

push-pro-server:
	docker tag $(pro_server_image) ${host}/$(pro_server_image)
	docker tag $(pro_server_image) ${host}/$(latest_pro_server_image)
	docker push ${host}/$(pro_server_image)
	docker push ${host}/$(latest_pro_server_image)

push: push-base push-server

.PHONY: base server push push-base push-server
