"""Shared pytest fixtures for AI Society Simulator tests.

This module provides reusable fixtures for setting up common test scenarios,
including worlds, agents, resources, and positions. The fixtures are designed
to be composable and minimize test setup duplication.
"""
import pytest
from typing import List, Tuple
import sys
import os

# Add src to path for imports
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

# Add world subpackage to path (needed for intra-package imports)
world_path = os.path.join(src_path, 'world')
sys.path.insert(0, world_path)

agents_path = os.path.join(src_path, 'agents')
sys.path.insert(0, agents_path)

resources_path = os.path.join(src_path, 'resources')
sys.path.insert(0, resources_path)

# Import after path adjustment - import only what's needed to avoid circular imports
from position import Position
# Delayed imports for fixtures that need them
# from terrain import TerrainTypeEnum, TerrainFactory
# from cell import StandardCell, BlockedCell
# from world import World, EagerWorld
# from resource import Food, Material, Water, ResourceType
# from factory import FoodFactory, MaterialFactory, WaterFactory, FactoryRegistry
# from traits import AgentTraits, TraitGenerator
# from basic_agent import BasicAgent


# ============================================================================
# SINGLETON RESET FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def reset_world_singleton():
    """Automatically reset World singleton before each test.

    This is critical for test isolation when testing the Singleton pattern.
    Without this, tests would interfere with each other.

    The fixture runs automatically before each test (autouse=True),
    resets the singleton after the test completes, and ensures clean state.
    """
    yield
    # Cleanup after test - import here to avoid circular imports
    try:
        from world import World
        World.reset_singleton()
    except:
        pass  # If World not imported yet, no need to reset


# ============================================================================
# POSITION FIXTURES
# ============================================================================

@pytest.fixture
def position_origin() -> Position:
    """Provide origin position (0, 0)."""
    return Position(0, 0)


@pytest.fixture
def position_center() -> Position:
    """Provide center position (5, 5)."""
    return Position(5, 5)


@pytest.fixture
def position_adjacent() -> Position:
    """Provide position adjacent to origin (1, 0)."""
    return Position(1, 0)


@pytest.fixture
def position_list() -> List[Position]:
    """Provide list of test positions."""
    return [
        Position(0, 0),
        Position(5, 5),
        Position(10, 10),
        Position(3, 7),
        Position(15, 2)
    ]


# ============================================================================
# TERRAIN & CELL FIXTURES
# ============================================================================

@pytest.fixture
def terrain_factory():
    """Provide initialized TerrainFactory."""
    TerrainFactory._initialize_defaults()
    return TerrainFactory


@pytest.fixture
def standard_cell(position_origin) -> StandardCell:
    """Provide a standard traversable cell at origin."""
    return StandardCell(position_origin, TerrainTypeEnum.PLAINS)


@pytest.fixture
def blocked_cell(position_origin) -> BlockedCell:
    """Provide a blocked water cell at origin."""
    return BlockedCell(position_origin, TerrainTypeEnum.WATER)


@pytest.fixture
def forest_cell(position_center) -> StandardCell:
    """Provide a forest cell at center position."""
    return StandardCell(position_center, TerrainTypeEnum.FOREST)


# ============================================================================
# WORLD FIXTURES
# ============================================================================

@pytest.fixture
def small_world() -> EagerWorld:
    """Provide a small 10x10 eager world for testing.

    The world is pre-populated with standard plains cells for all positions.
    This provides a consistent, predictable testing environment.
    """
    world = EagerWorld(10, 10)
    # Populate with standard cells
    for x in range(10):
        for y in range(10):
            pos = Position(x, y)
            cell = StandardCell(pos, TerrainTypeEnum.PLAINS)
            world.set_cell(pos, cell)
    return world


@pytest.fixture
def world_with_resources(small_world) -> EagerWorld:
    """Provide a world with resources pre-placed at specific positions.

    Resources are placed at:
    - (2, 2): Food
    - (5, 5): Water
    - (7, 3): Material
    """
    factory = FactoryRegistry()

    # Add resources at specific positions
    positions_with_resources = [
        (Position(2, 2), ResourceType.FOOD),
        (Position(5, 5), ResourceType.WATER),
        (Position(7, 3), ResourceType.MATERIAL)
    ]

    for pos, resource_type in positions_with_resources:
        cell = small_world.get_cell(pos)
        resource = factory.create_resource(resource_type, pos.to_tuple())
        if cell and resource:
            cell.add_resource(resource)

    return small_world


# ============================================================================
# RESOURCE FIXTURES
# ============================================================================

@pytest.fixture
def food_resource(position_origin) -> Food:
    """Provide a food resource at origin with standard properties."""
    return Food(
        amount=100.0,
        max_amount=100.0,
        position=position_origin.to_tuple(),
        regeneration_rate=0.15
    )


@pytest.fixture
def material_resource(position_origin) -> Material:
    """Provide a material resource at origin with standard properties."""
    return Material(
        amount=150.0,
        max_amount=150.0,
        position=position_origin.to_tuple(),
        material_quality=1.0
    )


@pytest.fixture
def water_resource(position_origin) -> Water:
    """Provide a water resource at origin with standard properties."""
    return Water(
        amount=80.0,
        max_amount=80.0,
        position=position_origin.to_tuple()
    )


@pytest.fixture
def resource_factories() -> Tuple[FoodFactory, MaterialFactory, WaterFactory]:
    """Provide all resource factory types as a tuple."""
    return (
        FoodFactory(),
        MaterialFactory(),
        WaterFactory()
    )


@pytest.fixture
def factory_registry() -> FactoryRegistry:
    """Provide an initialized factory registry."""
    return FactoryRegistry()


# ============================================================================
# AGENT FIXTURES
# ============================================================================

@pytest.fixture
def balanced_traits() -> AgentTraits:
    """Provide balanced agent traits (all attributes = 0.5)."""
    return TraitGenerator.balanced_traits()


@pytest.fixture
def strong_traits() -> AgentTraits:
    """Provide traits for a strong agent (high strength, low intelligence)."""
    return AgentTraits(
        strength=0.9,
        intelligence=0.3,
        sociability=0.5,
        aggression=0.7,
        curiosity=0.4
    )


@pytest.fixture
def intelligent_traits() -> AgentTraits:
    """Provide traits for an intelligent agent (high intelligence, low strength)."""
    return AgentTraits(
        strength=0.3,
        intelligence=0.9,
        sociability=0.6,
        aggression=0.2,
        curiosity=0.8
    )


@pytest.fixture
def basic_agent(position_origin, balanced_traits) -> BasicAgent:
    """Provide a basic agent with balanced traits at origin."""
    return BasicAgent(
        name="TestAgent",
        position=position_origin,
        traits=balanced_traits
    )


@pytest.fixture
def low_energy_agent(position_origin, balanced_traits) -> BasicAgent:
    """Provide agent with low energy (20.0) for testing energy-dependent behavior."""
    agent = BasicAgent(
        name="LowEnergyAgent",
        position=position_origin,
        traits=balanced_traits
    )
    agent._energy = 20.0
    return agent


@pytest.fixture
def high_energy_agent(position_origin, balanced_traits) -> BasicAgent:
    """Provide agent with high energy (95.0) for testing."""
    agent = BasicAgent(
        name="HighEnergyAgent",
        position=position_origin,
        traits=balanced_traits
    )
    agent._energy = 95.0
    return agent


@pytest.fixture
def damaged_agent(position_origin, balanced_traits) -> BasicAgent:
    """Provide agent with reduced health (40.0) for testing damage/healing."""
    agent = BasicAgent(
        name="DamagedAgent",
        position=position_origin,
        traits=balanced_traits
    )
    agent._health = 40.0
    return agent


# ============================================================================
# ACTION FIXTURES
# ============================================================================

@pytest.fixture
def move_action_factory():
    """Provide factory function for creating move actions.

    Returns a function that creates MoveAction instances with given target position.
    This allows tests to create actions with different parameters easily.
    """
    from actions.move import MoveAction
    def create_move_action(target: Position) -> MoveAction:
        return MoveAction(target)
    return create_move_action


@pytest.fixture
def gather_action_factory():
    """Provide factory function for creating gather actions.

    Returns a function that creates GatherAction instances with optional resource type.
    """
    from actions.gather import GatherAction
    def create_gather_action(resource_type=None) -> GatherAction:
        return GatherAction(resource_type)
    return create_gather_action


@pytest.fixture
def rest_action():
    """Provide a rest action instance."""
    from actions.rest import RestAction
    return RestAction()


# ============================================================================
# POLICY FIXTURES
# ============================================================================

@pytest.fixture
def selfish_policy():
    """Provide a selfish policy instance."""
    from policies.selfish import SelfishPolicy
    return SelfishPolicy()


# ============================================================================
# INTEGRATION TEST FIXTURES
# ============================================================================

@pytest.fixture
def populated_world(small_world) -> Tuple[EagerWorld, List[BasicAgent]]:
    """Provide world with multiple agents and resources for integration tests.

    Setup:
    - 3 agents placed at different positions
    - Resources scattered throughout the world
    - Agents start with balanced traits

    Returns:
        Tuple of (world, list of agents)
    """
    factory = FactoryRegistry()
    agents = []

    # Create agents at different positions
    agent_positions = [
        Position(2, 2),
        Position(5, 5),
        Position(8, 8)
    ]

    for i, pos in enumerate(agent_positions):
        traits = TraitGenerator.balanced_traits()
        agent = BasicAgent(
            name=f"Agent_{i}",
            position=pos,
            traits=traits
        )
        agents.append(agent)

        # Place agent in world cell
        cell = small_world.get_cell(pos)
        if cell:
            cell.add_occupant(agent.agent_id)

    # Add resources near agents
    resource_placements = [
        (Position(2, 3), ResourceType.FOOD),
        (Position(5, 6), ResourceType.WATER),
        (Position(8, 7), ResourceType.MATERIAL),
        (Position(4, 4), ResourceType.FOOD)
    ]

    for pos, res_type in resource_placements:
        cell = small_world.get_cell(pos)
        resource = factory.create_resource(res_type, pos.to_tuple())
        if cell and resource:
            cell.add_resource(resource)

    return small_world, agents


@pytest.fixture
def agent_with_resources(basic_agent, small_world, factory_registry) -> Tuple[BasicAgent, EagerWorld]:
    """Provide agent in a world with resources at adjacent positions.

    Agent is at (0, 0) with resources at:
    - (1, 0): Food
    - (0, 1): Water

    Returns:
        Tuple of (agent, world)
    """
    # Place agent in world
    agent_pos = basic_agent.position
    cell = small_world.get_cell(agent_pos)
    if cell:
        cell.add_occupant(basic_agent.agent_id)

    # Add resources adjacent to agent
    food_pos = Position(1, 0)
    water_pos = Position(0, 1)

    food_cell = small_world.get_cell(food_pos)
    water_cell = small_world.get_cell(water_pos)

    if food_cell:
        food = factory_registry.create_resource(ResourceType.FOOD, food_pos.to_tuple())
        if food:
            food_cell.add_resource(food)

    if water_cell:
        water = factory_registry.create_resource(ResourceType.WATER, water_pos.to_tuple())
        if water:
            water_cell.add_resource(water)

    return basic_agent, small_world
