PLUGINS := plugin.video.annatel.tv plugin.video.annatel.tvvod repository.reouvenannatel

VERSION := $(shell xmllint --xpath "string(/addon/@version)" $(firstword $(PLUGINS))/addon.xml)

.PHONY: zip-all generate_md5

zip-all: $(addprefix zip-,$(PLUGINS))

zip-%:
	mkdir -p repo/$*
	zip -r repo/$*/$(notdir $*)-$(VERSION).zip $*

generate_md5:
	md5 -q addons.xml > addons.xml.md5
