Design Patterns
===============

This project demonstrates numerous design patterns from the Gang of Four and other
software engineering best practices.

SOLID Principles
----------------

Single Responsibility Principle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Used in:**

* ``src/world/markers.py``
* ``src/world/events.py``
* ``src/resources/resource.py``

Each class has a single, well-defined responsibility. EventLogger logs events,
marker interfaces mark one capability each.

Open/Closed Principle
~~~~~~~~~~~~~~~~~~~~~

**Used in:**

* ``src/resources/resource.py``
* ``src/world/cell.py``
* ``src/generators/world_generator.py``

New resource types and cell types can be added without modifying existing code.

Liskov Substitution Principle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Used in:**

* ``src/resources/factory.py``
* ``src/generators/generator_factory.py``
* ``src/world/cell.py``

All factory subclasses work the same way. FoodFactory can be swapped for
MaterialFactory anywhere.

Interface Segregation Principle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Used in:**

* ``src/world/markers.py``
* ``src/world/iterators.py``

Multiple small interfaces instead of one large interface. Classes only
implement what they need.

Dependency Inversion Principle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Used in:**

* ``src/world/world_facade.py``
* ``src/generators/world_generator.py``

Code depends on abstract classes, not concrete implementations. WorldFacade
works with any World subclass.

Creational Patterns
-------------------

Singleton
~~~~~~~~~

**Location:** ``src/world/world.py``

Only one world instance exists at a time. Thread-safe with reset capability for testing.

Immutable
~~~~~~~~~

**Locations:**

* ``src/world/position.py``
* ``src/world/terrain.py``
* ``src/generators/config.py``
* ``src/world/events.py``

Position coordinates are immutable. Can be used as dictionary keys and event
logs remain consistent.

Abstract Factory
~~~~~~~~~~~~~~~~

**Location:** ``src/generators/generator_factory.py``

Different world generation strategies (random vs clustered) are created by
different factories.

Factory Method
~~~~~~~~~~~~~~

**Locations:**

* ``src/resources/factory.py``
* ``src/world/terrain.py``

Each resource type has its own factory. Makes creating resources easier and
adding new types cleaner.

Marker Interface
~~~~~~~~~~~~~~~~

**Location:** ``src/world/markers.py``

**Interfaces:**

* IHarvestable
* ITraversable
* IDepletable
* IRegenerative
* IBlocksMovement
* IObservable
* IPersistent
* ICacheable
* IPoolable
* ILazyLoadable

Tag classes with capabilities without forcing method implementations. Enables
runtime type checking.

Proxy
~~~~~

**Location:** ``src/world/cell_proxy.py``

Lazy loading of cells. CachingCellProxy automatically unloads idle cells to
save memory.

Prototype
~~~~~~~~~

**Location:** ``src/resources/prototype.py``

Clone pre-made resource templates instead of building from scratch every time.

Object Pool
~~~~~~~~~~~

**Location:** ``src/resources/resource_pool.py``

Reuse resource objects instead of creating and destroying them constantly.
Reduces garbage collection overhead.

Builder (Partial)
~~~~~~~~~~~~~~~~~

**Location:** ``src/generators/config.py``

WorldConfig has builder-style methods like ``with_width()`` and ``with_height()``.

Structural Patterns
-------------------

Iterator
~~~~~~~~

**Location:** ``src/world/iterators.py``

Multiple ways to traverse the grid:

* All cells
* Cells within radius
* Path traversal
* Spiral pattern
* Row-by-row

Facade
~~~~~~

**Location:** ``src/world/world_facade.py``

Simple interface for world operations. Hides complexity of World, Cell, and
Position interactions.

Bridge (Partial)
~~~~~~~~~~~~~~~~

**Location:** ``src/world/cell.py``

Cells and terrain are somewhat separated but not a full Bridge pattern
implementation.

Strategy (Partial)
~~~~~~~~~~~~~~~~~~

**Locations:**

* ``src/generators/generator_factory.py``
* ``src/resources/factory.py``
* ``src/world/iterators.py``

Algorithm selection through factories and iterators. Factory pattern already
provides needed functionality.

Other Patterns
--------------

Registry
~~~~~~~~

**Locations:**

* ``src/resources/factory.py``
* ``src/resources/prototype.py``
* ``src/generators/generator_factory.py``

Central lookup for factories, prototypes, and generators. Easy to register
new types.

Template Method (Implicit)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Location:** ``src/generators/world_generator.py``

WorldGenerator has common steps in base class, subclasses fill in specifics.
Not a formal implementation.

Summary
-------

**Fully Implemented: 16 patterns**

* SOLID principles (all 5)
* Singleton, Immutable, Abstract Factory, Factory Method
* Marker, Proxy, Prototype, Object Pool
* Iterator, Facade, Registry

**Partially Implemented: 4 patterns**

* Builder, Bridge, Strategy, Template Method
