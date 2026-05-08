# Environment
env-create:
	conda env create -f conda.yml

env-update:
	conda env update -f conda.yml --prune

# Dependencies
deps-pre:
	pip install pip-tools

deps-compile: deps-pre
	pip-compile --resolver=backtracking requirements.in