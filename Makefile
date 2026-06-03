.PHONY: dev lint format compile smoke verify clean all

# Install engine runtime deps + lint tooling
dev:
	pip install pyyaml pypdf ruff

# Lint / format the deterministic engine
lint:
	ruff check engine

format:
	ruff format engine

# Byte-compile every engine script (fast sanity check)
compile:
	python -m py_compile engine/*.py

# Full pipeline against a staged config.yaml + work/ (render -> build -> verify gate)
smoke:
	python engine/render_resumes.py
	python engine/render_coverletters.py
	python engine/render_linkedin.py
	python engine/render_strategy.py
	python engine/build_pdfs.py
	python engine/verify.py

# Just the verify gate (assumes output/ already built)
verify:
	python engine/verify.py

clean:
	rm -rf .ruff_cache .mypy_cache __pycache__ engine/__pycache__

all: compile lint
