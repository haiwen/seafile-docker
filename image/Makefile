server_version=6.0.5

base_image=seafileorg/base:16.04
server_image=seafileorg/server:$(server_version)

all:
	@echo
	@echo Pleaes use '"make base"' or '"make server"' or '"make push"'.
	@echo

base:
	cd base && docker build -t $(base_image) .

server:
	cd seafile && docker build -t $(server_image) .

push:
	docker push $(base_image)
	docker push $(server_image)

.PHONY: base server push
