"""
Resources Package - Resource management and creation

Exports resource classes, factories, prototypes, and pool management.
"""

from .resource import Resource, Food, Material, Water, ResourceType
from .factory import (
    ResourceFactory,
    FoodFactory,
    MaterialFactory,
    WaterFactory,
    RandomResourceFactory,
    FactoryRegistry
)
from .prototype import (
    IPrototype,
    ResourcePrototype,
    PrototypeRegistry,
    create_default_prototypes
)
from .resource_pool import (
    ObjectPool,
    ResourcePool,
    PoolManager
)

__all__ = [
    # Resources
    'Resource',
    'Food',
    'Material',
    'Water',
    'ResourceType',

    # Factories
    'ResourceFactory',
    'FoodFactory',
    'MaterialFactory',
    'WaterFactory',
    'RandomResourceFactory',
    'FactoryRegistry',

    # Prototypes
    'IPrototype',
    'ResourcePrototype',
    'PrototypeRegistry',
    'create_default_prototypes',

    # Object Pool
    'ObjectPool',
    'ResourcePool',
    'PoolManager',
]
