.PHONY: dev lint format compile validate smoke verify clean all

# Install engine runtime deps + lint tooling (jsonschema optional; tools fall back without it)
dev:
	pip install pyyaml pypdf ruff jsonschema

# Lint / format the deterministic engine
lint:
	ruff check engine

format:
	ruff format engine

# Byte-compile every engine script (fast sanity check)
compile:
	python -m py_compile engine/*.py engine/tools/*.py

# Validate work/*.json against the schemas + content hygiene (deterministic guardrails)
validate:
	python engine/tools/validate.py
	python engine/tools/rulecheck.py

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
