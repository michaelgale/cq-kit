#!/usr/bin/env bash
black cqkit/*.py
black tests/*.py
pre-commit run --all-files
