VERSION       := $(shell cat VERSION)
BINARY_NAME   := "mariadb_filters.wasm"
RELEASE_NAME  := mariadb_filters-$(VERSION)
TARBALL_NAME  := mariadb_filters-$(VERSION).tar.gz

all: build

clean:
	rm -f mariadb_filters.wasm || true

.PHONY: build
build: clean
	tinygo build -target=wasi -o $(BINARY_NAME) filters.go

.PHONY: package 
package: build
	tar -cvzf $(TARBALL_NAME) $(BINARY_NAME) && rm $(BINARY_NAME)

.PHONY: release
release: package
	gh release delete $(RELEASE_NAME) -y || true
	gh release create $(RELEASE_NAME) --notes "$(RELEASE_NAME)"
	gh release upload $(RELEASE_NAME) $(TARBALL_NAME) --clobber
