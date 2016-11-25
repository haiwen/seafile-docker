server_version=6.0.5

base_image=seafileorg/base:16.04
base_image_squashed=seafileorg/base:16.04-squashed
server_image=seafileorg/server:$(server_version)

all:
	@echo
	@echo Pleaes use '"make base"' or '"make server"' or '"make push"'.
	@echo

base:
	cd base && docker build -t $(base_image) .

server:
	cd seafile && docker build -t $(server_image) .

squash-base:
	docker-squash --verbose --tag $(base_image_squashed) $(base_image)
	docker tag $(base_image_squashed) $(base_image)

push:
	docker push $(base_image)
	docker push $(server_image)

.PHONY: base server push
