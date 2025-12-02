#!/usr/bin/env bash
set -euo pipefail

# Lightweight smoke test to ensure the simulation driver runs without errors.
python -m src.main --steps 2 --world-width 6 --world-height 6 --basic-agents 1 --learning-agents 1 --ai-agents 0 --npc-agents 0 --resource-density 0.1
