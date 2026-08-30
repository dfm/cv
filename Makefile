all:
	scripts/update-astro-pubs
	scripts/update-github-repos
	scripts/render
	scripts/format-markdown
	git --no-pager diff

tex:
	cd tex && make

.PHONY: all tex
