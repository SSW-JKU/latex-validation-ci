lint:
	pylint latex_validation_action
	pylint tests

typecheck:
	mypy -p latex_validation_action
	mypy -p tests

test:
	pytest -v tests

all: lint typecheck test
