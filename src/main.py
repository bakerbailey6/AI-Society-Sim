"""Entrypoint script for running the AI Society simulation.

This module parses CLI arguments, builds a world, seeds resources and agents,
sets up social systems, economy, and inventory, then runs a full simulation
using the SimulationEngine.

The simulation integrates:
- World and terrain generation
- Agent spawning with inventories and traits
- Social systems (factions, relationships, reputation)
- Economy (marketplace with dynamic pricing)
- Simulation engine with scheduling and analytics
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Ensure legacy absolute imports inside package modules resolve correctly when run as a module
BASE_DIR = os.path.dirname(__file__)
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, "world"))
sys.path.append(os.path.join(BASE_DIR, "agents"))
sys.path.append(os.path.join(BASE_DIR, "resources"))

# Ensure shared module instances for legacy absolute imports used throughout the codebase
import world.position as world_position
import world.terrain as world_terrain
import world.markers as world_markers

sys.modules.setdefault("position", world_position)
sys.modules.setdefault("terrain", world_terrain)
sys.modules.setdefault("markers", world_markers)

# Core imports
from agents.agent_factory import AgentFactoryRegistry
from agents.agent_manager import AgentManager
from agents.traits import TraitGenerator
from resources.factory import FactoryRegistry
from resources.resource import ResourceType
from world.cell import BlockedCell, StandardCell
from world.events import EventLogger, WorldStateChangedEvent
from position import Position
from terrain import TerrainTypeEnum, TerrainFactory
from world.world import EagerWorld, LazyWorld, World
from world.world_facade import WorldFacade

# Simulation engine imports
from simulation.engine import (
    SimulationEngine,
    SimulationConfig as EngineConfig,
    SimulationObserver,
    SimulationEvent,
    SimulationEventType,
)
from simulation.scheduler import (
    SchedulingStrategy,
    SequentialScheduler,
    RandomScheduler,
    PriorityScheduler,
    RoundRobinScheduler,
)
from simulation.analytics import AnalyticsCollector

# Economy imports
from economy.marketplace import Marketplace, MarketplaceConfig
from economy.pricing import FixedPricing, SupplyDemandPricing

# Social system imports
from social.relationships import InMemoryRelationshipManager, RelationshipType
from social.reputation import InMemoryReputationManager, ReputationTier
from social.factory import FactionFactory, GroupFactory, create_faction
from social.faction import GovernanceType

# Inventory imports
from inventory.inventory import Inventory
from inventory.resource_stack import ResourceStack
from inventory.capacity_strategy import (
    SlotBasedCapacity,
    WeightBasedCapacity,
    CompositeCapacity,
)

DEFAULT_TERRAIN_DISTRIBUTION = {
    "plains": 0.4,
    "forest": 0.3,
    "mountain": 0.2,
    "water": 0.1,
}


@dataclass(frozen=True)
class SimulationConfig:
    """Configuration for the simulation."""
    # World settings
    width: int
    height: int
    seed: Optional[int]
    resource_density: float
    world_type: str

    # Simulation settings
    steps: int
    scheduler: str
    stop_on_extinction: bool

    # Agent settings
    basic_agents: int
    learning_agents: int
    ai_agents: int
    npc_agents: int

    # Economy settings
    enable_marketplace: bool
    pricing_strategy: str

    # Social settings
    enable_factions: bool
    initial_factions: int

    # Output settings
    log_file: Optional[Path]
    verbose: bool


def parse_args() -> SimulationConfig:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run the AI Society simulation",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # World settings
    world_group = parser.add_argument_group("World Settings")
    world_group.add_argument("--world-width", type=int, default=12, help="Width of the world grid")
    world_group.add_argument("--world-height", type=int, default=12, help="Height of the world grid")
    world_group.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    world_group.add_argument(
        "--resource-density", type=float, default=0.25,
        help="Chance (0-1) that a traversable cell starts with a resource",
    )
    world_group.add_argument(
        "--world-type", choices=["eager", "lazy"], default="eager",
        help="World loading strategy",
    )

    # Simulation settings
    sim_group = parser.add_argument_group("Simulation Settings")
    sim_group.add_argument("--steps", type=int, default=10, help="Number of simulation steps")
    sim_group.add_argument(
        "--scheduler", choices=["sequential", "random", "priority", "round-robin"],
        default="round-robin", help="Agent scheduling strategy",
    )
    sim_group.add_argument(
        "--stop-on-extinction", action="store_true", default=True,
        help="Stop simulation if all agents die",
    )

    # Agent settings
    agent_group = parser.add_argument_group("Agent Settings")
    agent_group.add_argument("--basic-agents", type=int, default=4, help="Number of basic agents")
    agent_group.add_argument("--learning-agents", type=int, default=2, help="Number of learning agents")
    agent_group.add_argument("--ai-agents", type=int, default=1, help="Number of AI agents")
    agent_group.add_argument("--npc-agents", type=int, default=2, help="Number of NPC agents")

    # Economy settings
    economy_group = parser.add_argument_group("Economy Settings")
    economy_group.add_argument(
        "--enable-marketplace", action="store_true", default=True,
        help="Enable the marketplace for trading",
    )
    economy_group.add_argument(
        "--pricing-strategy", choices=["fixed", "supply-demand"], default="supply-demand",
        help="Marketplace pricing strategy",
    )

    # Social settings
    social_group = parser.add_argument_group("Social Settings")
    social_group.add_argument(
        "--enable-factions", action="store_true", default=True,
        help="Enable faction system",
    )
    social_group.add_argument(
        "--initial-factions", type=int, default=2,
        help="Number of initial factions to create",
    )

    # Output settings
    output_group = parser.add_argument_group("Output Settings")
    output_group.add_argument(
        "--log-file", type=Path, default=None,
        help="Path to write event log",
    )
    output_group.add_argument(
        "--verbose", "-v", action="store_true", default=False,
        help="Enable verbose output",
    )

    args = parser.parse_args()
    return SimulationConfig(
        width=args.world_width,
        height=args.world_height,
        seed=args.seed,
        resource_density=args.resource_density,
        world_type=args.world_type,
        steps=args.steps,
        scheduler=args.scheduler,
        stop_on_extinction=args.stop_on_extinction,
        basic_agents=args.basic_agents,
        learning_agents=args.learning_agents,
        ai_agents=args.ai_agents,
        npc_agents=args.npc_agents,
        enable_marketplace=args.enable_marketplace,
        pricing_strategy=args.pricing_strategy,
        enable_factions=args.enable_factions,
        initial_factions=args.initial_factions,
        log_file=args.log_file,
        verbose=args.verbose,
    )


def _choose_terrain() -> TerrainTypeEnum:
    """Randomly select a terrain type based on distribution weights."""
    names = list(DEFAULT_TERRAIN_DISTRIBUTION.keys())
    weights = list(DEFAULT_TERRAIN_DISTRIBUTION.values())
    chosen = random.choices(names, weights=weights)[0]
    return {
        "plains": TerrainTypeEnum.PLAINS,
        "forest": TerrainTypeEnum.FOREST,
        "mountain": TerrainTypeEnum.MOUNTAIN,
        "water": TerrainTypeEnum.WATER,
    }[chosen]


def build_world(config: SimulationConfig, logger: EventLogger) -> Tuple[World, WorldFacade]:
    """Build the world with terrain and initial resources."""
    world_cls = EagerWorld if config.world_type == "eager" else LazyWorld
    world = world_cls(config.width, config.height)
    factory = FactoryRegistry()
    TerrainFactory._initialize_defaults()

    for x in range(config.width):
        for y in range(config.height):
            position = Position(x, y)
            terrain_type = _choose_terrain()
            if terrain_type == TerrainTypeEnum.WATER:
                cell = BlockedCell(position, terrain_type)
            else:
                cell = StandardCell(position, terrain_type, max_resources=3, max_occupants=5)

            if terrain_type != TerrainTypeEnum.WATER and random.random() < config.resource_density:
                resource_type = random.choice(list(ResourceType))
                resource = factory.create_resource(resource_type, position.to_tuple())
                if resource:
                    cell.add_resource(resource)

            world.set_cell(position, cell)

    return world, WorldFacade(world)


def _iter_traversable_cells(world: World):
    """Iterate over all traversable cells in the world."""
    for pos in world.get_all_cells_iterator():
        cell = world.get_cell(pos)
        if isinstance(cell, StandardCell) and cell.is_traversable():
            yield pos, cell


def create_agent_inventory(agent_id: str, agent_name: str, traits: dict) -> Inventory:
    """Create an inventory for an agent based on their traits."""
    # Calculate capacity based on strength trait
    strength = traits.get("strength", 50) if isinstance(traits, dict) else getattr(traits, "strength", 50)
    base_weight = 20.0  # Base carry weight in kg
    weight_capacity = base_weight + (strength * 0.5)  # Higher strength = more carry capacity

    # Create composite capacity: both slot and weight limits
    capacity = CompositeCapacity([
        SlotBasedCapacity(max_slots=20),
        WeightBasedCapacity(max_weight=weight_capacity),
    ])

    return Inventory(agent_id, capacity, f"{agent_name}'s Inventory")


def give_starting_resources(inventory: Inventory) -> None:
    """Give an agent some starting resources."""
    # Give each agent a small amount of starting food and water
    food_stack = ResourceStack(
        resource_type=ResourceType.FOOD,
        quantity=random.uniform(5.0, 15.0),
        metadata=("starting_food",),
    )
    water_stack = ResourceStack(
        resource_type=ResourceType.WATER,
        quantity=random.uniform(3.0, 10.0),
        metadata=("starting_water",),
    )
    inventory.add(food_stack)
    inventory.add(water_stack)


def spawn_agents(
    config: SimulationConfig,
    agent_manager: AgentManager,
    world: World,
) -> Dict[str, Inventory]:
    """Spawn agents and create their inventories."""
    registry = AgentFactoryRegistry()
    counts: Dict[str, int] = {
        "basic": config.basic_agents,
        "learning": config.learning_agents,
        "ai": config.ai_agents,
        "npc": config.npc_agents,
    }

    traversable_cells = list(_iter_traversable_cells(world))
    if not traversable_cells:
        raise RuntimeError("No traversable cells available for agent placement")

    agent_inventories: Dict[str, Inventory] = {}
    agent_index = 1

    for agent_type, count in counts.items():
        for _ in range(count):
            position, cell = random.choice(traversable_cells)
            traits = TraitGenerator.random_traits()
            agent = registry.create_agent(
                agent_type,
                f"{agent_type.title()}-{agent_index}",
                position,
                traits=traits,
            )
            agent_manager.register_agent(agent)
            cell.add_occupant(agent.agent_id)

            # Create inventory for the agent
            inventory = create_agent_inventory(agent.agent_id, agent.name, traits)
            give_starting_resources(inventory)
            agent_inventories[agent.agent_id] = inventory

            agent_index += 1

    return agent_inventories


def create_scheduler(scheduler_name: str) -> SchedulingStrategy:
    """Create a scheduling strategy by name."""
    schedulers = {
        "sequential": SequentialScheduler,
        "random": RandomScheduler,
        "priority": PriorityScheduler,
        "round-robin": RoundRobinScheduler,
    }
    scheduler_cls = schedulers.get(scheduler_name, RoundRobinScheduler)
    return scheduler_cls()


def create_marketplace(config: SimulationConfig) -> Optional[Marketplace]:
    """Create and configure the marketplace."""
    if not config.enable_marketplace:
        return None

    # Choose pricing strategy
    if config.pricing_strategy == "supply-demand":
        pricing = SupplyDemandPricing()
    else:
        pricing = FixedPricing()

    marketplace_config = MarketplaceConfig(
        default_offer_duration=None,  # No expiry for offers
        min_offer_quantity=0.1,
        max_active_offers=10,
        enable_price_tracking=True,
        transaction_fee_rate=0.0,  # No transaction fees
    )

    return Marketplace(pricing, marketplace_config)


def create_initial_factions(
    config: SimulationConfig,
    agent_manager: AgentManager,
    reputation_manager: InMemoryReputationManager,
) -> Dict[str, any]:
    """Create initial factions and assign some agents to them."""
    if not config.enable_factions or config.initial_factions <= 0:
        return {}

    factions = {}
    living_agents = list(agent_manager.get_living_agents())

    if len(living_agents) < config.initial_factions:
        logging.warning("Not enough agents to create %d factions", config.initial_factions)
        return {}

    # Create factions with different governance types
    governance_types = [
        GovernanceType.DEMOCRACY,
        GovernanceType.AUTOCRACY,
        GovernanceType.OLIGARCHY,
        GovernanceType.MERITOCRACY,
    ]

    faction_names = [
        "The Pioneers",
        "Iron Brotherhood",
        "Forest Guardians",
        "Mountain Clan",
        "River Folk",
    ]

    # Assign founding agents to factions
    random.shuffle(living_agents)

    for i in range(min(config.initial_factions, len(faction_names))):
        founder = living_agents[i]
        gov_type = governance_types[i % len(governance_types)]

        faction = create_faction(
            name=faction_names[i],
            founder_id=founder.agent_id,
            timestamp=0.0,
            governance_type=gov_type,
        )

        factions[faction.entity_id] = faction

        # Set the founder's initial reputation with their faction
        reputation_manager.set_reputation(
            founder.agent_id,
            faction.entity_id,
            value=200.0,  # Start with FRIENDLY standing
            reason="Faction founder",
            timestamp=0.0,
        )

        logging.info(
            "Created faction '%s' (%s) with founder %s",
            faction.name, gov_type.name, founder.name
        )

    # Optionally assign some other agents to factions
    remaining_agents = living_agents[config.initial_factions:]
    faction_list = list(factions.values())

    for agent in remaining_agents:
        if random.random() < 0.5 and faction_list:  # 50% chance to join a faction
            faction = random.choice(faction_list)
            # Set initial neutral-to-friendly reputation
            reputation_manager.set_reputation(
                agent.agent_id,
                faction.entity_id,
                value=random.uniform(0.0, 150.0),
                reason="Initial faction membership",
                timestamp=0.0,
            )

    return factions


def initialize_relationships(
    agent_manager: AgentManager,
    relationship_manager: InMemoryRelationshipManager,
) -> None:
    """Initialize some random relationships between agents."""
    agents = list(agent_manager.get_living_agents())

    # Create a few random initial relationships
    for agent in agents:
        # Each agent knows about 1-3 other agents initially
        num_relationships = random.randint(1, min(3, len(agents) - 1))
        other_agents = [a for a in agents if a.agent_id != agent.agent_id]

        for other in random.sample(other_agents, min(num_relationships, len(other_agents))):
            # Random initial relationship strength (-20 to +40)
            strength = random.uniform(-20.0, 40.0)
            relationship_manager.set_relationship(
                agent.agent_id,
                other.agent_id,
                RelationshipType.ACQUAINTANCE,
                strength,
                timestamp=0.0,
            )


class ConsoleObserver(SimulationObserver):
    """Observer that logs simulation events to console."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def on_event(self, event: SimulationEvent) -> None:
        if event.event_type == SimulationEventType.STEP_COMPLETED:
            if self.verbose:
                step = event.data.get("step", 0)
                agents = event.data.get("agents", 0)
                duration = event.data.get("duration_ms", 0)
                logging.info("Step %d completed: %d agents, %.2fms", step, agents, duration)
        elif event.event_type == SimulationEventType.COMPLETED:
            reason = event.data.get("reason", "unknown")
            logging.info("Simulation completed: %s", reason)


def safe_agent_step(agent_manager: AgentManager, world: World, event_logger: EventLogger) -> int:
    """Execute one step for all agents, handling errors gracefully."""
    actions_taken = 0
    for agent in agent_manager.get_living_agents():
        try:
            agent.update(world)
            actions_taken += 1
        except NotImplementedError:
            event_logger.log_event(
                WorldStateChangedEvent(
                    timestamp=world.current_time,
                    event_type="agent_skipped",
                    description=f"Skipped update for {agent.name} (behavior not implemented)",
                    change_type="agent_step",
                    affected_positions=(agent.position.to_tuple(),),
                    metadata={"agent_id": agent.agent_id, "agent_type": agent.__class__.__name__},
                )
            )
    return actions_taken


def count_resources(world: World) -> int:
    """Count total resources in the world."""
    total = 0
    for _pos in world.get_all_cells_iterator():
        cell = world.get_cell(_pos)
        if cell:
            total += len(cell.resources)
    return total


def get_inventory_summary(inventories: Dict[str, Inventory]) -> Dict[str, float]:
    """Get summary of all agent inventories."""
    total_by_type: Dict[ResourceType, float] = {}
    for inventory in inventories.values():
        for resource_type, quantity in inventory.get_resource_summary().items():
            if resource_type not in total_by_type:
                total_by_type[resource_type] = 0.0
            total_by_type[resource_type] += quantity

    return {rt.name: qty for rt, qty in total_by_type.items()}


def summarize(
    agent_manager: AgentManager,
    world: World,
    inventories: Dict[str, Inventory],
    factions: Dict[str, any],
    relationship_manager: InMemoryRelationshipManager,
    marketplace: Optional[Marketplace],
) -> Dict[str, any]:
    """Generate comprehensive simulation summary."""
    summary = {
        "simulation": {
            "steps": world.current_time,
            "events_logged": world.event_logger.get_event_count(),
        },
        "agents": {
            "total": agent_manager.count_agents(),
            "living": agent_manager.count_living_agents(),
            "dead": agent_manager.count_dead_agents(),
        },
        "world": {
            "total_resources": count_resources(world),
        },
        "inventories": get_inventory_summary(inventories),
        "social": {
            "factions": len(factions),
            "faction_names": [f.name for f in factions.values()] if factions else [],
        },
    }

    if marketplace:
        summary["economy"] = marketplace.get_statistics()

    return summary


def write_log(log_file: Path, event_logger: EventLogger) -> None:
    """Write event log to file."""
    lines = [str(event) for event in event_logger.get_events()]
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text("\n".join(lines), encoding="utf-8")


def run_simulation(config: SimulationConfig) -> Dict[str, any]:
    """Run the full simulation."""
    if config.seed is not None:
        random.seed(config.seed)

    # Create world
    logging.info("Creating world (%sx%s, %s)", config.width, config.height, config.world_type)
    world, facade = build_world(config, EventLogger())

    # Create agent manager and spawn agents
    agent_manager = AgentManager()
    inventories = spawn_agents(config, agent_manager, world)
    logging.info("Spawned %d agents with inventories", agent_manager.count_agents())

    # Create social systems
    relationship_manager = InMemoryRelationshipManager()
    reputation_manager = InMemoryReputationManager()

    # Initialize relationships between agents
    initialize_relationships(agent_manager, relationship_manager)
    logging.info("Initialized agent relationships")

    # Create factions
    factions = create_initial_factions(config, agent_manager, reputation_manager)
    if factions:
        logging.info("Created %d factions", len(factions))

    # Create marketplace
    marketplace = create_marketplace(config)
    if marketplace:
        logging.info("Marketplace enabled with %s pricing", config.pricing_strategy)

    # Create scheduler
    scheduler = create_scheduler(config.scheduler)
    logging.info("Using %s scheduler", config.scheduler)

    # Create simulation engine configuration
    engine_config = EngineConfig(
        max_steps=config.steps,
        step_delay_ms=0.0,
        enable_analytics=True,
        stop_on_extinction=config.stop_on_extinction,
        random_seed=config.seed,
    )

    # Create simulation engine
    engine = SimulationEngine(
        world=world,
        agents=list(agent_manager.get_living_agents()),
        config=engine_config,
        scheduler=scheduler,
        marketplace=marketplace,
    )

    # Add console observer for progress
    engine.add_observer(ConsoleObserver(verbose=config.verbose))

    # Run simulation
    logging.info("Starting simulation for %d steps", config.steps)

    # Use a hybrid approach: engine orchestrates, but we handle agent updates manually
    # since the engine's step() has placeholder implementation
    for step in range(config.steps):
        world.update()
        actions = safe_agent_step(agent_manager, world, world.event_logger)

        # Clean up expired offers in marketplace
        if marketplace:
            marketplace.cleanup_expired_offers()

        # Clean up expired relationship modifiers
        relationship_manager.cleanup_expired_modifiers(world.current_time)

        if config.verbose:
            logging.info(
                "Step %d: %d agents, %d actions",
                step + 1, agent_manager.count_living_agents(), actions
            )

        # Check for extinction
        if config.stop_on_extinction and agent_manager.count_living_agents() == 0:
            logging.info("All agents have died - stopping simulation")
            break

    # Generate summary
    results = summarize(
        agent_manager, world, inventories, factions,
        relationship_manager, marketplace
    )
    logging.info("Simulation finished")

    # Write log file if requested
    if config.log_file:
        write_log(config.log_file, world.event_logger)
        logging.info("Wrote event log to %s", os.fspath(config.log_file))

    return results


def print_summary(results: Dict[str, any]) -> None:
    """Print formatted simulation summary."""
    print("\n" + "=" * 50)
    print("SIMULATION SUMMARY")
    print("=" * 50)

    # Simulation info
    sim = results.get("simulation", {})
    print(f"\nSimulation:")
    print(f"  Steps completed: {sim.get('steps', 0)}")
    print(f"  Events logged: {sim.get('events_logged', 0)}")

    # Agent info
    agents = results.get("agents", {})
    print(f"\nAgents:")
    print(f"  Total: {agents.get('total', 0)}")
    print(f"  Living: {agents.get('living', 0)}")
    print(f"  Dead: {agents.get('dead', 0)}")

    # World info
    world_info = results.get("world", {})
    print(f"\nWorld:")
    print(f"  Resources remaining: {world_info.get('total_resources', 0)}")

    # Inventory summary
    inventories = results.get("inventories", {})
    if inventories:
        print(f"\nAgent Inventories (total):")
        for resource, quantity in inventories.items():
            print(f"  {resource}: {quantity:.1f}")

    # Social info
    social = results.get("social", {})
    if social.get("factions"):
        print(f"\nFactions ({social.get('factions', 0)}):")
        for name in social.get("faction_names", []):
            print(f"  - {name}")

    # Economy info
    economy = results.get("economy", {})
    if economy:
        print(f"\nMarketplace:")
        print(f"  Active offers: {economy.get('active_offers', 0)}")
        print(f"  Total trades: {economy.get('total_trades', 0)}")
        print(f"  Pricing strategy: {economy.get('pricing_strategy', 'N/A')}")

    print("\n" + "=" * 50)


def main() -> None:
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
    )

    config = parse_args()

    if config.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    results = run_simulation(config)
    print_summary(results)

    if config.log_file:
        print(f"\nEvent log saved to: {config.log_file}")


if __name__ == "__main__":
    main()
