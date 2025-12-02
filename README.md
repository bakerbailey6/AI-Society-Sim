# Emergent AI Society Simulator

**CS455 Design Patterns - Final Project**

A multi-agent simulation demonstrating emergent societal behaviors through autonomous agent interactions in a shared world environment.

## Overview

The Emergent AI Society Simulator showcases how simple autonomous agents can produce complex societal behaviors like economies, factions, and conflicts through their interactions. Agents begin in a primitive Stone Age and can progress through technological eras (Agricultural → Industrial) as they innovate and cooperate. This project emphasizes clean architecture and design patterns with text-based output for analysis.

## Features

### Core Simulation
- **Grid World Environment**: Agents exist in a resource-rich world with food, materials, and water
- **Agent Traits**: Each agent has unique characteristics including strength, intelligence, and sociability
- **Discrete Time Steps**: Simulation progresses through structured time intervals
- **Emergent Behaviors**: Complex societal patterns emerge from simple interaction rules

### Agent Behavior System
Agents follow a three-phase behavioral cycle:
1. **Sense**: Detect nearby resources, other agents, and environmental threats
2. **Decide**: Choose actions based on their decision policy (selfish, cooperative, AI-driven)
3. **Act**: Execute chosen actions like gathering, trading, moving, attacking, or forming alliances

### Technological Progression
- **Stone Age**: Basic survival, hunting/gathering, small tribal structures
- **Agricultural Era**: Farming development, permanent settlements, larger populations, increased trade
- **Industrial Era**: Specialization, advanced production systems, complex societies

Technology spreads through discovery, learning from others, and trade networks.

### Emergent Outcomes
From simple behavioral rules, complex patterns emerge:
- Economic markets and sophisticated trade networks
- Social hierarchies and factional systems
- Territorial competition and resource conflicts
- Knowledge diffusion across different societies

### Analysis & Reporting
- **Event Logging**: Comprehensive tracking of trades, conflicts, alliances, and technological discoveries
- **End Reports**: Detailed analysis of wealth distribution, faction stability, and technology timelines
- **Strategy Comparison**: Evaluation of different agent strategies and their societal outcomes

## Architecture

The project demonstrates key design patterns through a clean, modular architecture:

### Core Components

#### Simulation Engine
- Main simulation loop managing world state
- Environment and world management systems
- Comprehensive event logging infrastructure

#### Agent System
- **Abstract Agent class**: Base implementation for all agent types
- **Concrete Implementations**: BasicAgent, LearningAgent, AIAgent
- **Strategy Pattern**: Decision policies (Selfish, Cooperative, Aggressive)

#### Technology System
- **State Pattern**: Abstract TechEra class managing technological progression
- **Concrete Eras**: StoneAge, AgriculturalEra, IndustrialEra implementations
- **Tech Mechanics**: Discovery and diffusion systems

#### Social Systems
- **Composite Pattern**: Groups and Factions management
- **Trade Marketplace**: Economic interaction systems
- **Conflict Resolution**: Dispute and warfare mechanics

#### Action System
- **Command Pattern**: Abstract Action class for all executable actions
- **Concrete Actions**: Move, Gather, Trade, Attack, FormAlliance

## Running the simulation driver

The repository now includes a small command-line driver that wires together the
world, agent factories, and event logger for quick experiments.

### Quickstart

```bash
python -m src.main --steps 5 --world-width 12 --world-height 12 --basic-agents 3 --learning-agents 1 --ai-agents 1 --npc-agents 1
```

### Common options

- `--world-width`, `--world-height`: Grid dimensions (default `12x12`).
- `--steps`: Number of simulation steps to execute (default `5`).
- `--seed`: Random seed for reproducible layouts and agent placement.
- `--world-type`: Choose `eager` (default) or `lazy` world implementations.
- `--resource-density`: Probability a traversable cell starts with a resource (default `0.25`).
- `--basic-agents`, `--learning-agents`, `--ai-agents`, `--npc-agents`: How many of each agent type to spawn.
- `--log-file`: Optional path to write the event log for offline inspection.

At the end of the run, a summary of steps completed, agent counts, and total
resources is printed to stdout. When `--log-file` is provided, the textual event
stream is written to the requested location.

### Smoke test

To verify the entrypoint runs in your environment, execute the bundled script:

```bash
bash scripts/smoke_test.sh
```

The script runs a two-step simulation on a small map and will exit non-zero if
any errors occur.

