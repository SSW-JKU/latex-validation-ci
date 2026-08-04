lint:
# 	pylint latex_validation_action
	pylint tests
	pylint action_tests

typecheck:
# 	mypy -p latex_validation_action
	mypy -p tests
	mypy -p action_tests

test:
	pytest -v tests

all: lint typecheck test
