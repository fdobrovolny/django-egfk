.PHONY: docs release clean build

%.txt: %.md
	pandoc -o $@ $<

%:
	README.txt CHANGELOG.txt

README.txt: README.md

CHANGELOG.txt: CHANGELOG.md

docs: README.txt CHANGELOG.txt
	sphinx-build -aE docs build/docs > /dev/null

release:
	