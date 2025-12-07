# Design Patterns

Documentation of design patterns used in this project.

---

## SOLID Principles

### Single Responsibility Principle
**Used**

**Where:**
- [src/world/markers.py](src/world/markers.py)
- [src/world/events.py](src/world/events.py)
- [src/resources/resource.py](src/resources/resource.py)

**Why:**
Each class does one thing. EventLogger logs events, marker interfaces mark one capability each.

---

### Open/Closed Principle
**Used**

**Where:**
- [src/resources/resource.py](src/resources/resource.py:45-167)
- [src/world/cell.py](src/world/cell.py:31-245)
- [src/generators/world_generator.py](src/generators/world_generator.py)

**Why:**
Can add new resource types and cell types without changing existing code.

---

### Liskov Substitution Principle
**Used**

**Where:**
- [src/resources/factory.py](src/resources/factory.py:26-85)
- [src/generators/generator_factory.py](src/generators/generator_factory.py:62-121)
- [src/world/cell.py](src/world/cell.py)

**Why:**
All the factory subclasses work the same way. Can swap FoodFactory for MaterialFactory anywhere.

---

### Interface Segregation Principle
**Used**

**Where:**
- [src/world/markers.py](src/world/markers.py)
- [src/world/iterators.py](src/world/iterators.py:23-71)

**Why:**
Lots of small interfaces instead of one big one. Classes only implement what they actually need.

---

### Dependency Inversion Principle
**Used**

**Where:**
- [src/world/world_facade.py](src/world/world_facade.py:51)
- [src/generators/world_generator.py](src/generators/world_generator.py:25)

**Why:**
Code depends on abstract classes, not concrete ones. WorldFacade works with any World subclass.

---

## Creational Patterns

### Singleton
**Used**

**Where:**
- [src/world/world.py:27-56](src/world/world.py#L27-L56)
- [src/world/world.py:58-286](src/world/world.py#L58-L286)

**Why:**
Only need one world at a time. Thread-safe with reset for testing.

---

### Immutable
**Used**

**Where:**
- [src/world/position.py:21](src/world/position.py#L21)
- [src/world/terrain.py:45](src/world/terrain.py#L45)
- [src/generators/config.py:20](src/generators/config.py#L20)
- [src/world/events.py:23](src/world/events.py#L23)

**Why:**
Position coords shouldn't change. Can use them as dict keys and event logs won't get messed up.

---

### Abstract Factory
**Used**

**Where:**
- [src/generators/generator_factory.py:24-60](src/generators/generator_factory.py#L24-L60)
- [src/generators/generator_factory.py:62-121](src/generators/generator_factory.py#L62-L121)

**Why:**
Different world generation strategies (random vs clustered) get created by different factories.

---

### Factory Method
**Used**

**Where:**
- [src/resources/factory.py:26-85](src/resources/factory.py#L26-L85)
- [src/resources/factory.py:87-312](src/resources/factory.py#L87-L312)
- [src/world/terrain.py:89-212](src/world/terrain.py#L89-L212)

**Why:**
Each resource type has its own factory. Makes creating resources easier and adding new types cleaner.

---

### Marker
**Used**

**Where:**
- [src/world/markers.py](src/world/markers.py)

**Interfaces:**
- IHarvestable
- ITraversable
- IDepletable
- IRegenerative
- IBlocksMovement
- IObservable
- IPersistent
- ICacheable
- IPoolable
- ILazyLoadable

**Why:**
Tag classes with capabilities without forcing them to implement methods. Can check types at runtime.

---

### Proxy
**Used**

**Where:**
- [src/world/cell_proxy.py:30-258](src/world/cell_proxy.py#L30-L258)
- [src/world/cell_proxy.py:260-317](src/world/cell_proxy.py#L260-L317)
- [src/world/cell_proxy.py:319-388](src/world/cell_proxy.py#L319-L388)

**Why:**
Don't load every cell into memory. Load them when needed. CachingCellProxy unloads idle cells automatically.

---

### Prototype
**Used**

**Where:**
- [src/resources/prototype.py:24-47](src/resources/prototype.py#L24-L47)
- [src/resources/prototype.py:49-157](src/resources/prototype.py#L49-L157)
- [src/resources/prototype.py:159-280](src/resources/prototype.py#L159-L280)

**Why:**
Clone pre-made resource templates instead of building from scratch every time.

---

### Object Pool
**Used**

**Where:**
- [src/resources/resource_pool.py:28-80](src/resources/resource_pool.py#L28-L80)
- [src/resources/resource_pool.py:82-295](src/resources/resource_pool.py#L82-L295)
- [src/resources/resource_pool.py:297-426](src/resources/resource_pool.py#L297-L426)

**Why:**
Reuse resource objects instead of creating and destroying them constantly. Less garbage collection.

---

### Builder
**Partially used**

**Where:**
- [src/generators/config.py:65-118](src/generators/config.py#L65-L118)

**Why:**
WorldConfig has builder-style methods like with_width() and with_height(). Didn't need a full separate builder class.

---

## Structural Patterns

### Iterator
**Used**

**Where:**
- [src/world/iterators.py:23-71](src/world/iterators.py#L23-L71)
- [src/world/iterators.py:73-127](src/world/iterators.py#L73-L127)
- [src/world/iterators.py:129-212](src/world/iterators.py#L129-L212)
- [src/world/iterators.py:215-258](src/world/iterators.py#L215-L258)
- [src/world/iterators.py:260-343](src/world/iterators.py#L260-L343)

**Why:**
Different ways to traverse the grid (all cells, radius, path, spiral) without exposing grid internals.

---

### Facade
**Used**

**Where:**
- [src/world/world_facade.py:28-333](src/world/world_facade.py#L28-L333)

**Why:**
Simple interface for world operations. Don't need to understand how World, Cell, Position all work together.

---

### Bridge
**Partially used**

**Where:**
- [src/world/cell.py](src/world/cell.py)

**Why:**
Cells and terrain are somewhat separated but not a full Bridge pattern. Works fine as is.

---

### Strategy
**Used**

**Where:**
- [src/policies/policy.py](src/policies/policy.py#L18-L122)
- [src/policies/selfish.py](src/policies/selfish.py)
- [src/policies/cooperative.py](src/policies/cooperative.py) (skeleton)
- [src/policies/aggressive.py](src/policies/aggressive.py) (skeleton)

**Why:**
Decision policies are interchangeable strategies that can be swapped at runtime. Agents can change behavior by switching policies (selfish → cooperative → aggressive).

---

## Behavioral Patterns

### Command
**Used**

**Where:**
- [src/actions/action.py](src/actions/action.py#L28-L189)
- [src/actions/move.py](src/actions/move.py)
- [src/actions/gather.py](src/actions/gather.py)
- [src/actions/rest.py](src/actions/rest.py)
- [src/actions/trade.py](src/actions/trade.py) (skeleton)
- [src/actions/attack.py](src/actions/attack.py) (skeleton)
- [src/actions/alliance.py](src/actions/alliance.py) (skeleton)

**Why:**
Agent actions are encapsulated as command objects with execute(), can_execute(), and undo() methods. Enables queuing, logging, and undoable operations.

---

## Other Patterns

### Registry
**Used**

**Where:**
- [src/resources/factory.py:409-471](src/resources/factory.py#L409-L471)
- [src/resources/prototype.py:159-280](src/resources/prototype.py#L159-L280)
- [src/generators/generator_factory.py:123-203](src/generators/generator_factory.py#L123-L203)

**Why:**
Central place to look up factories, prototypes, and generators. Easy to add new types.

---

### Template Method
**Used**

**Where:**
- [src/generators/world_generator.py:33-266](src/generators/world_generator.py#L33-L266)
- [src/agents/agent.py](src/agents/agent.py) - Agent.update() lifecycle
- [src/social/social_entity.py](src/social/social_entity.py) - join/leave operations

**Why:**
WorldGenerator has common steps in base class, subclasses fill in specifics. Agent.update() orchestrates sense-decide-act cycle. SocialEntity.join()/leave() define flow with hooks for subclasses.

---

### Observer
**Used**

**Where:**
- [src/inventory/observers.py](src/inventory/observers.py) - Inventory change notifications
- [src/social/social_entity.py](src/social/social_entity.py) - SocialEntityObserver for membership changes
- [src/social/relationships.py](src/social/relationships.py) - RelationshipObserver
- [src/social/reputation.py](src/social/reputation.py) - ReputationObserver

**Why:**
Decouple event sources from listeners. Inventory changes, membership changes, relationship updates, and reputation changes all notify interested parties without tight coupling.

---

## Social System Patterns

### Abstract Base Class (Social Entities)
**Used**

**Where:**
- [src/social/social_entity.py](src/social/social_entity.py) - SocialEntity base class
- [src/social/faction.py](src/social/faction.py) - Faction extends SocialEntity
- [src/social/group.py](src/social/group.py) - Group extends SocialEntity

**Why:**
Defines common interface for all social structures (factions, groups, alliances). Subclasses implement specific behavior while sharing membership management logic.

---

### Strategy (Governance)
**Used**

**Where:**
- [src/social/faction.py](src/social/faction.py) - GovernanceStrategy, AutocracyGovernance, OligarchyGovernance, DemocracyGovernance, MeritocracyGovernance

**Why:**
Factions can have different governance styles that affect decision-making, succession, and authority. Swap governance at design time or runtime.

---

### Strategy (Reputation Effects)
**Used**

**Where:**
- [src/social/reputation.py](src/social/reputation.py) - ReputationEffects, StandardReputationEffects

**Why:**
Different factions can apply different effects based on reputation tier. Trade modifiers, service access, and territory restrictions vary by strategy.

---

### Factory Method (Social Entities)
**Used**

**Where:**
- [src/social/factory.py](src/social/factory.py) - SocialEntityFactory, FactionFactory, GroupFactory

**Why:**
Encapsulate creation of factions and groups with sensible defaults. Convenience methods like create_hunting_party() for common configurations.

---

### Registry (Social Entity Factories)
**Used**

**Where:**
- [src/social/factory.py](src/social/factory.py) - SocialEntityFactoryRegistry

**Why:**
Central lookup for social entity factories by type. Singleton pattern with reset for testing.

---

### Flyweight (Governance Strategies)
**Used**

**Where:**
- [src/social/factory.py](src/social/factory.py) - FactionFactory._governance_strategies

**Why:**
Governance strategy instances are stateless and shared across all factions of the same governance type. Reduces memory usage.

---

### Immutable (Social Records)
**Used**

**Where:**
- [src/social/social_entity.py](src/social/social_entity.py) - Membership dataclass
- [src/social/relationships.py](src/social/relationships.py) - RelationshipModifier
- [src/social/reputation.py](src/social/reputation.py) - ReputationChange, ReputationThresholds

**Why:**
Membership records, relationship modifiers, and reputation change events should not be modified after creation. Ensures audit trail integrity.

---

## Summary

**Fully implemented:** 24 patterns
- SOLID principles (all 5)
- Creational: Singleton, Immutable, Abstract Factory, Factory Method, Marker, Proxy, Prototype, Object Pool, Flyweight
- Structural: Iterator, Facade, Registry
- Behavioral: Command, Strategy, Template Method, Observer

**Social System patterns:** 8 patterns
- Abstract Base Class, Strategy (Governance), Strategy (Reputation Effects)
- Factory Method, Registry, Flyweight, Immutable, Observer

**Partially implemented:** 2 patterns
- Builder, Bridge

**Note:** Template Method is now formally used in Agent.update(), WorldGenerator, and SocialEntity join/leave operations.
