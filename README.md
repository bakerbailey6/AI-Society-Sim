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

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/AI-Society-Sim.git
   cd AI-Society-Sim
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Documentation

This project includes comprehensive Sphinx documentation covering:
- Architecture and design patterns
- API reference for all modules
- Usage examples and guides

### Building Documentation

To build the HTML documentation locally:

**On Windows:**
```bash
cd docs
sphinx-build -M html . _build
```

**On Linux/Mac:**
```bash
cd docs
make html
```

The generated documentation will be available at `docs/_build/html/index.html`. Open this file in your web browser to view the documentation.

### Viewing Documentation

After building, open the documentation in your browser:
```bash
# Windows
start docs/_build/html/index.html

# Mac
open docs/_build/html/index.html

# Linux
xdg-open docs/_build/html/index.html
```

### ReadTheDocs

The documentation is also available online at ReadTheDocs (coming soon).

## Design Patterns

This project demonstrates 16 fully implemented design patterns and 4 partially implemented patterns. For detailed documentation of all patterns used, see:
- [Patterns.md](Patterns.md) - Quick reference guide
- Full documentation in `docs/design_patterns.rst`

## Contributing

Contributions are welcome! Please ensure your code follows the established design patterns and includes appropriate documentation.

## License

This project is part of CS455 Design Patterns coursework.

