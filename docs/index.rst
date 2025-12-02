Emergent AI Society Simulator Documentation
============================================

Welcome to the Emergent AI Society Simulator documentation!

A multi-agent simulation demonstrating emergent societal behaviors through
autonomous agent interactions in a shared world environment.

**CS455 Design Patterns - Final Project**

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   architecture
   design_patterns
   api/modules

Overview
--------

The Emergent AI Society Simulator showcases how simple autonomous agents can
produce complex societal behaviors like economies, factions, and conflicts
through their interactions. Agents begin in a primitive Stone Age and can
progress through technological eras (Agricultural → Industrial) as they
innovate and cooperate.

Key Features
~~~~~~~~~~~~

* **Grid World Environment**: Agents exist in a resource-rich world
* **Agent Traits**: Unique characteristics including strength, intelligence, and sociability
* **Discrete Time Steps**: Structured time interval progression
* **Emergent Behaviors**: Complex societal patterns from simple interaction rules
* **Technological Progression**: Stone Age → Agricultural Era → Industrial Era
* **Social Systems**: Trade, alliances, factions, and conflicts

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/yourusername/AI-Society-Sim.git
   cd AI-Society-Sim
   pip install -r requirements.txt

Building Documentation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd docs
   make html

The documentation will be generated in ``docs/_build/html/``.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
