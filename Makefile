all:
	uv run scripts/update-astro-pubs
	uv run scripts/update-github-repos
	uv run scripts/render
	cd tex && pandoc -s cv.tex -o ../README.md --template=template.markdown --to=gfm
	uv run scripts/format-markdown
	git --no-pager diff

tex:
	cd tex && make

.PHONY: all tex
