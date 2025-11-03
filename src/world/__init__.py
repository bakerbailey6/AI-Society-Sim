"""
World Package - Core world management and grid system

Exports key classes for world, cells, positions, and iterators.
"""

from .position import Position
from .terrain import TerrainTypeEnum, TerrainProperties, TerrainFactory
from .cell import Cell, StandardCell, BlockedCell, LazyCell
from .cell_proxy import CellProxy, CachingCellProxy, ProtectedCellProxy
from .world import World, EagerWorld, LazyWorld, SingletonMeta
from .world_facade import WorldFacade
from .iterators import (
    GridIterator,
    AllCellsIterator,
    RadiusIterator,
    PathIterator,
    SpiralIterator
)
from .events import (
    WorldEvent,
    ResourceDepletedEvent,
    ResourceRegeneratedEvent,
    TimeStepEvent,
    CellAccessedEvent,
    WorldStateChangedEvent,
    EventLogger
)
from .markers import (
    IHarvestable,
    ITraversable,
    IDepletable,
    IRegenerative,
    IBlocksMovement,
    IObservable,
    IPersistent,
    ICacheable,
    IPoolable,
    ILazyLoadable
)

__all__ = [
    # Position and Terrain
    'Position',
    'TerrainTypeEnum',
    'TerrainProperties',
    'TerrainFactory',

    # Cells
    'Cell',
    'StandardCell',
    'BlockedCell',
    'LazyCell',

    # Proxies
    'CellProxy',
    'CachingCellProxy',
    'ProtectedCellProxy',

    # World
    'World',
    'EagerWorld',
    'LazyWorld',
    'SingletonMeta',
    'WorldFacade',

    # Iterators
    'GridIterator',
    'AllCellsIterator',
    'RadiusIterator',
    'PathIterator',
    'SpiralIterator',

    # Events
    'WorldEvent',
    'ResourceDepletedEvent',
    'ResourceRegeneratedEvent',
    'TimeStepEvent',
    'CellAccessedEvent',
    'WorldStateChangedEvent',
    'EventLogger',

    # Markers
    'IHarvestable',
    'ITraversable',
    'IDepletable',
    'IRegenerative',
    'IBlocksMovement',
    'IObservable',
    'IPersistent',
    'ICacheable',
    'IPoolable',
    'ILazyLoadable',
]
