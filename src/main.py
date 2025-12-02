"""Entrypoint script for running a lightweight AI Society simulation.

This module parses CLI arguments, builds a world, seeds resources and agents,
and runs a simple simulation loop that exercises the existing world and agent
infrastructure. The defaults are intentionally small so that a quick demo runs
fast while still producing meaningful output.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple

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

DEFAULT_TERRAIN_DISTRIBUTION = {
    "plains": 0.4,
    "forest": 0.3,
    "mountain": 0.2,
    "water": 0.1,
}


@dataclass(frozen=True)
class SimulationConfig:
    width: int
    height: int
    steps: int
    seed: Optional[int]
    resource_density: float
    world_type: str
    basic_agents: int
    learning_agents: int
    ai_agents: int
    npc_agents: int
    log_file: Optional[Path]


def parse_args() -> SimulationConfig:
    parser = argparse.ArgumentParser(description="Run a simple AI Society simulation")
    parser.add_argument("--world-width", type=int, default=12, help="Width of the world grid")
    parser.add_argument("--world-height", type=int, default=12, help="Height of the world grid")
    parser.add_argument("--steps", type=int, default=5, help="Number of simulation steps to execute")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument(
        "--resource-density",
        type=float,
        default=0.25,
        help="Chance (0-1) that a traversable cell starts with a resource",
    )
    parser.add_argument(
        "--world-type",
        choices=["eager", "lazy"],
        default="eager",
        help="Select whether to pre-load cells (eager) or use lazy world container",
    )
    parser.add_argument("--basic-agents", type=int, default=3, help="Number of basic agents to spawn")
    parser.add_argument(
        "--learning-agents", type=int, default=1, help="Number of learning agents to spawn"
    )
    parser.add_argument("--ai-agents", type=int, default=1, help="Number of AI agents to spawn")
    parser.add_argument("--npc-agents", type=int, default=1, help="Number of NPC agents to spawn")
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Optional path to write a textual log of simulation events",
    )

    args = parser.parse_args()
    return SimulationConfig(
        width=args.world_width,
        height=args.world_height,
        steps=args.steps,
        seed=args.seed,
        resource_density=args.resource_density,
        world_type=args.world_type,
        basic_agents=args.basic_agents,
        learning_agents=args.learning_agents,
        ai_agents=args.ai_agents,
        npc_agents=args.npc_agents,
        log_file=args.log_file,
    )


def _choose_terrain() -> TerrainTypeEnum:
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
    for pos in world.get_all_cells_iterator():
        cell = world.get_cell(pos)
        if isinstance(cell, StandardCell) and cell.is_traversable():
            yield pos, cell


def spawn_agents(config: SimulationConfig, agent_manager: AgentManager, world: World) -> None:
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
            agent_index += 1


def safe_agent_step(agent_manager: AgentManager, world: World, event_logger: EventLogger) -> None:
    for agent in agent_manager.get_living_agents():
        try:
            agent.update(world)
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


def count_resources(world: World) -> int:
    total = 0
    for _pos in world.get_all_cells_iterator():
        cell = world.get_cell(_pos)
        if cell:
            total += len(cell.resources)
    return total


def summarize(agent_manager: AgentManager, world: World) -> Dict[str, int]:
    return {
        "steps": world.current_time,
        "total_agents": agent_manager.count_agents(),
        "living_agents": agent_manager.count_living_agents(),
        "dead_agents": agent_manager.count_dead_agents(),
        "total_resources": count_resources(world),
        "events_logged": world.event_logger.get_event_count(),
    }


def write_log(log_file: Path, event_logger: EventLogger) -> None:
    lines = [str(event) for event in event_logger.get_events()]
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text("\n".join(lines), encoding="utf-8")


def run_simulation(config: SimulationConfig) -> Dict[str, int]:
    if config.seed is not None:
        random.seed(config.seed)

    logging.info("Creating world (%sx%s, %s)", config.width, config.height, config.world_type)
    world, _facade = build_world(config, EventLogger())
    agent_manager = AgentManager()
    spawn_agents(config, agent_manager, world)

    logging.info("Starting simulation for %s steps", config.steps)
    for _ in range(config.steps):
        world.update()
        safe_agent_step(agent_manager, world, world.event_logger)

    results = summarize(agent_manager, world)
    logging.info("Simulation finished: %s", results)

    if config.log_file:
        write_log(config.log_file, world.event_logger)
        logging.info("Wrote event log to %s", os.fspath(config.log_file))

    return results


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    config = parse_args()
    results = run_simulation(config)

    print("\nSimulation Summary")
    print("------------------")
    for key, value in results.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

    if config.log_file:
        print(f"\nEvent log saved to: {config.log_file}")


if __name__ == "__main__":
    main()
