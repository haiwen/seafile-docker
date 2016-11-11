version=6.0.5

all:
	cd seafile && docker build -t seafileorg/server:$(version) .

base:
	cd base && docker build -t seafileorg/base:16.04 .

.PHONY: base
