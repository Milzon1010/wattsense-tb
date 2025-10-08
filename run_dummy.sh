#!/usr/bin/env bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python dummy_to_tb.py
