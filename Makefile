compile:
	pybabel compile -d locales/

run: compile
	python -m app

lint:
	ruff check --fix
	ruff format

update-messages:
	pybabel extract app -o locales/messages.pot -k Message
	pybabel update -i locales/messages.pot -d locales/
	pybabel compile -d locales/

add-locale:
	pybabel extract app -o locales/messages.pot -k Message
	pybabel init -i locales/messages.pot -d locales -l $(LOCALE)

.PHONY: compile run lint update-messages add-locale