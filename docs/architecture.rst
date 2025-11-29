Architecture
============

The project demonstrates key design patterns through a clean, modular architecture.

Core Components
---------------

Simulation Engine
~~~~~~~~~~~~~~~~~

The simulation engine manages the main simulation loop and world state:

* Main simulation loop managing world state
* Environment and world management systems
* Comprehensive event logging infrastructure

Agent System
~~~~~~~~~~~~

The agent system implements autonomous entities with different behaviors:

* **Abstract Agent class**: Base implementation for all agent types
* **Concrete Implementations**: BasicAgent, LearningAgent, AIAgent
* **Strategy Pattern**: Decision policies (Selfish, Cooperative, Aggressive)

Technology System
~~~~~~~~~~~~~~~~~

The technology system manages technological progression:

* **State Pattern**: Abstract TechEra class managing technological progression
* **Concrete Eras**: StoneAge, AgriculturalEra, IndustrialEra implementations
* **Tech Mechanics**: Discovery and diffusion systems

Social Systems
~~~~~~~~~~~~~~

Social systems handle group dynamics and interactions:

* **Composite Pattern**: Groups and Factions management
* **Trade Marketplace**: Economic interaction systems
* **Conflict Resolution**: Dispute and warfare mechanics

Action System
~~~~~~~~~~~~~

The action system implements executable agent actions:

* **Command Pattern**: Abstract Action class for all executable actions
* **Concrete Actions**: Move, Gather, Trade, Attack, FormAlliance

Module Structure
----------------

The codebase is organized into the following modules:

World Module
~~~~~~~~~~~~

* ``world.py``: Main world implementation
* ``world_facade.py``: Simplified interface to world operations
* ``cell.py``: Grid cell implementation
* ``cell_proxy.py``: Proxy pattern for cell access control
* ``position.py``: Position and coordinate handling
* ``terrain.py``: Terrain types and properties
* ``events.py``: Event system for tracking world events
* ``markers.py``: Markers for special world locations
* ``iterators.py``: Iterator patterns for world traversal

Resources Module
~~~~~~~~~~~~~~~~

* ``resource.py``: Base resource classes
* ``prototype.py``: Prototype pattern for resource creation
* ``factory.py``: Factory pattern for resource generation
* ``resource_pool.py``: Resource pool management

Generators Module
~~~~~~~~~~~~~~~~~

* ``world_generator.py``: World generation logic
* ``generator_factory.py``: Factory for world generators
* ``config.py``: Configuration for world generation
