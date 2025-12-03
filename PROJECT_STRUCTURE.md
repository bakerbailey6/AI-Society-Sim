# Project Structure - AI Society Simulator

## Overview
This document provides a guide to the World/Environment system architecture and file organization.

## Directory Structure

```
AI-Society-Sim/
├── src/                          # Source code
│   ├── __init__.py              # Package root
│   ├── world/                    # World and grid management
│   │   ├── __init__.py
│   │   ├── position.py          # Immutable Position class
│   │   ├── terrain.py           # Terrain types and properties
│   │   ├── events.py            # World event system
│   │   ├── markers.py           # Marker interfaces
│   │   ├── cell.py              # Abstract Cell and implementations
│   │   ├── cell_proxy.py        # Proxy pattern for lazy loading
│   │   ├── iterators.py         # Iterator pattern for grid traversal
│   │   ├── world.py             # Singleton World class
│   │   └── world_facade.py      # Facade pattern for simple access
│   ├── resources/                # Resource management
│   │   ├── __init__.py
│   │   ├── resource.py          # Abstract Resource hierarchy
│   │   ├── factory.py           # Factory Method pattern
│   │   ├── prototype.py         # Prototype pattern
│   │   └── resource_pool.py     # Object Pool pattern
│   ├── generators/               # World generation
│   │   ├── __init__.py
│   │   ├── config.py            # Immutable WorldConfig
│   │   ├── world_generator.py   # Abstract generators
│   │   └── generator_factory.py # Abstract Factory pattern
│   ├── agents/                   # Agent system
│   │   ├── __init__.py
│   │   ├── agent.py             # Abstract Agent base class
│   │   ├── basic_agent.py       # Simple rule-based agent
│   │   ├── learning_agent.py    # Q-learning/RL agent (skeleton)
│   │   ├── ai_agent.py          # LLM-powered agent (skeleton)
│   │   ├── npc_agent.py         # Scripted behavior agent (skeleton)
│   │   ├── agent_factory.py     # Factory Method pattern
│   │   ├── agent_manager.py     # Agent lifecycle management
│   │   └── traits.py            # Agent characteristics
│   ├── actions/                  # Action system (Command pattern) ✓ IMPLEMENTED
│   │   ├── __init__.py
│   │   ├── action.py            # Abstract Action base class
│   │   ├── move.py              # Move to new position
│   │   ├── gather.py            # Collect resources
│   │   ├── rest.py              # Recover energy
│   │   ├── trade.py             # Exchange resources (skeleton)
│   │   ├── attack.py            # Combat actions (skeleton)
│   │   └── alliance.py          # Form alliances (skeleton)
│   ├── policies/                 # Decision policies (Strategy pattern) ✓ IMPLEMENTED
│   │   ├── __init__.py
│   │   ├── policy.py            # Abstract DecisionPolicy base class
│   │   ├── selfish.py           # Individual survival strategy
│   │   ├── cooperative.py       # Group benefit strategy (skeleton)
│   │   └── aggressive.py        # Competitive strategy (skeleton)
│   ├── social/                   # Social systems (NEW)
│   │   ├── __init__.py
│   │   ├── group.py             # Composite pattern for groups
│   │   ├── faction.py           # Faction management
│   │   ├── relationship.py      # Inter-agent relationships
│   │   ├── communication.py     # Observer pattern for messages
│   │   └── alliance.py          # Alliance mechanics
│   ├── technology/               # Technology system (NEW)
│   │   ├── __init__.py
│   │   ├── tech_era.py          # State pattern for tech eras
│   │   ├── tech_tree.py         # Technology dependency graph
│   │   ├── innovation.py        # Discovery mechanics
│   │   └── knowledge_base.py    # Agent knowledge storage
│   ├── economy/                  # Economic system (NEW)
│   │   ├── __init__.py
│   │   ├── inventory.py         # Resource storage
│   │   ├── trade.py             # Trade mechanics
│   │   ├── marketplace.py       # Mediator pattern for trading
│   │   └── pricing.py           # Dynamic price calculation
│   └── simulation/               # Simulation engine (NEW)
│       ├── __init__.py
│       ├── engine.py            # Main simulation loop
│       ├── scheduler.py         # Agent update ordering
│       └── analytics.py         # Data collection and analysis
├── docs/                         # Generated Sphinx documentation (to be created)
├── README.md                     # Project overview
├── AI_AGENT_DESIGN.md            # Comprehensive agent design document (NEW)
├── Patterns.md                   # Design patterns documentation
├── PROJECT_STRUCTURE.md          # This file
└── requirements.txt              # Python dependencies

```

## File Descriptions

### World Package (`src/world/`)

#### position.py
- **Pattern:** Immutable
- **Purpose:** Immutable 2D coordinate representation
- **Key Classes:** `Position`
- **Features:** Distance calculations, neighbor finding, bounds checking

#### terrain.py
- **Pattern:** Immutable, Flyweight-like caching
- **Purpose:** Terrain type definitions and properties
- **Key Classes:** `TerrainTypeEnum`, `TerrainProperties`, `TerrainFactory`
- **Features:** Terrain types (plains, forest, mountain, water, desert)

#### events.py
- **Pattern:** Immutable event objects
- **Purpose:** Event system for tracking world changes
- **Key Classes:** `WorldEvent`, `ResourceDepletedEvent`, `TimeStepEvent`, `EventLogger`
- **Features:** Immutable event records, event filtering

#### markers.py
- **Pattern:** Marker Interface
- **Purpose:** Type-based capability marking
- **Key Interfaces:** `IHarvestable`, `ITraversable`, `IDepletable`, `IRegenerative`, `IBlocksMovement`, `IObservable`, `IPoolable`, `ILazyLoadable`
- **Features:** Runtime type checking, capability indication

#### cell.py
- **Pattern:** Abstract base class with concrete implementations
- **Purpose:** Grid cell representation
- **Key Classes:** `Cell` (abstract), `StandardCell`, `BlockedCell`, `LazyCell`
- **Features:** Resource storage, occupant tracking, terrain properties

#### cell_proxy.py
- **Pattern:** Proxy
- **Purpose:** Lazy loading and access control for cells
- **Key Classes:** `CellProxy`, `CachingCellProxy`, `ProtectedCellProxy`
- **Features:** Deferred loading, auto-unloading, access validation

#### iterators.py
- **Pattern:** Iterator
- **Purpose:** Grid traversal strategies
- **Key Classes:** `GridIterator` (abstract), `AllCellsIterator`, `RadiusIterator`, `PathIterator`, `SpiralIterator`
- **Features:** Multiple iteration patterns for different use cases

#### world.py
- **Pattern:** Singleton
- **Purpose:** Central world management
- **Key Classes:** `SingletonMeta`, `World` (abstract), `EagerWorld`, `LazyWorld`
- **Features:** Single world instance, time progression, event logging

#### world_facade.py
- **Pattern:** Facade
- **Purpose:** Simplified world access interface
- **Key Classes:** `WorldFacade`
- **Features:** Simple methods for common operations, reduced coupling

### Resources Package (`src/resources/`)

#### resource.py
- **Pattern:** Abstract hierarchy with marker interfaces
- **Purpose:** Resource type definitions
- **Key Classes:** `Resource` (abstract), `Food`, `Material`, `Water`, `ResourceType` enum
- **Features:** Different resource behaviors, regeneration, depletion

#### factory.py
- **Pattern:** Factory Method
- **Purpose:** Resource creation abstraction
- **Key Classes:** `ResourceFactory` (abstract), `FoodFactory`, `MaterialFactory`, `WaterFactory`, `RandomResourceFactory`, `FactoryRegistry`
- **Features:** Type-specific creation, random generation, centralized registry

#### prototype.py
- **Pattern:** Prototype
- **Purpose:** Resource template cloning
- **Key Classes:** `IPrototype`, `ResourcePrototype`, `PrototypeRegistry`, `create_default_prototypes()`
- **Features:** Template-based creation, efficient cloning, preset templates

#### resource_pool.py
- **Pattern:** Object Pool
- **Purpose:** Resource object reuse
- **Key Classes:** `ObjectPool` (abstract), `ResourcePool`, `PoolManager`
- **Features:** Object reuse, memory efficiency, multi-pool management

### Generators Package (`src/generators/`)

#### config.py
- **Pattern:** Immutable
- **Purpose:** World generation configuration
- **Key Classes:** `WorldConfig`, factory functions for standard configs
- **Features:** Immutable configuration, builder-style with_* methods

#### world_generator.py
- **Pattern:** Factory Method, Template Method
- **Purpose:** World generation algorithms
- **Key Classes:** `WorldGenerator` (abstract), `RandomWorldGenerator`, `ClusteredWorldGenerator`
- **Features:** Different generation strategies, configurable density

#### generator_factory.py
- **Pattern:** Abstract Factory
- **Purpose:** Generator creation abstraction
- **Key Classes:** `GeneratorFactory` (abstract), `RandomGeneratorFactory`, `ClusteredGeneratorFactory`, `GeneratorFactoryRegistry`, `create_default_world()`
- **Features:** Family of related generators, registry management, convenience functions

## Design Pattern Summary

### Patterns Used (15 total)

1. **SOLID Principles** (5) - Applied throughout
2. **Singleton** - World instance
3. **Factory Method** - Resource creation
4. **Abstract Factory** - Generator families
5. **Prototype** - Resource cloning
6. **Object Pool** - Resource reuse
7. **Proxy** - Lazy loading cells
8. **Facade** - Simplified world interface
9. **Iterator** - Grid traversal
10. **Immutable** - Value objects
11. **Marker** - Capability interfaces

## Key Relationships

### Dependency Flow
```
generators → world → cell → resources
                 ↓
              events
                 ↓
              markers
```

### Pattern Interactions
- **Singleton + Facade**: World singleton accessed via facade
- **Factory + Prototype**: Factories can use prototypes
- **Proxy + Iterator**: Proxied cells can be iterated
- **Pool + Factory**: Factories can return pooled instances

## Next Steps (Future Work)

1. **Generate Sphinx Documentation**
   - Run `sphinx-quickstart` in `docs/` directory
   - Configure for NumPy/Google docstring style
   - Generate HTML documentation

2. **Create Test Suite**
   - Unit tests for each pattern
   - Integration tests for subsystem interaction
   - Coverage reports

3. **Expand to Other Subsystems**
   - Agent system (State pattern, Strategy pattern, Command pattern)
   - Technology system (State pattern for tech eras)
   - Social systems (Composite pattern for groups)

4. **Add Concrete Implementations**
   - Fill in abstract method bodies where appropriate
   - Add actual simulation logic
   - Integrate all subsystems

## Usage Examples

### Creating a World
```python
from src.generators import create_default_world

# Create a medium-sized world with clustered resources
world = create_default_world(size='medium', generator_type='clustered', seed=42)
```

### Using the Facade
```python
from src.world import WorldFacade

facade = WorldFacade(world)
facade.place_resource_at((10, 15), ResourceType.FOOD, amount=100.0)
resources = facade.get_nearby_resources((10, 15), radius=5)
```

### Iterating the Grid
```python
from src.world import RadiusIterator, Position

iterator = RadiusIterator(Position(50, 50), radius=10, width=100, height=100)
for pos in iterator:
    cell = world.get_cell(pos)
    # Process cell
```

## Documentation

- **README.md**: High-level project overview
- **Patterns.md**: Detailed design pattern documentation
- **PROJECT_STRUCTURE.md**: This file - architecture guide
- **Code docstrings**: Sphinx-compatible documentation in all files
