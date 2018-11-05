server_version=6.3.4

base_image=seafileltd/base:pi
base_image_squashed=seafileltd/base:pi-squashed
server_image=seafileltd/seafile:$(server_version)-pi
server_image_squashed=seafileltd/seafile:$(server_version)-pi-squashed

all:
	@echo
	@echo Please use '"make base"' or '"make server"' or '"make push"'.
	@echo

base:
	docker pull ubuntu:18.04
	cd base && docker build -t $(base_image) .
	docker-squash --tag $(base_image_squashed) $(base_image)
	docker tag $(base_image_squashed) $(base_image)
	docker rmi `docker images --filter "dangling=true" -q --no-trunc`

server:
	cd seafile && cp -rf ../../scripts ./ && docker build -t $(server_image) .
	docker-squash --tag $(server_image_squashed) $(server_image) --from-layer=$(base_image)
	docker tag $(server_image_squashed) $(server_image)
	docker tag $(server_image) $(latest_server_image)
	docker rmi `docker images --filter "dangling=true" -q --no-trunc`

push-server:
	docker push $(server_image)
	docker push $(latest_server_image)

push: push-base push-server

.PHONY: base server push push-base push-server
