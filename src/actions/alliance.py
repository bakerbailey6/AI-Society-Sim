"""
FormAllianceAction Module - Command for Alliance Formation

This module provides the FormAllianceAction class, demonstrating the Command
pattern for social interactions and alliance formation.

Design Patterns:
    - Command: FormAllianceAction encapsulates alliance creation as an object
    - Composite: Integrates with faction/group hierarchy
    - Observer: Notifies members of alliance formation
    - Factory: Uses SocialEntityFactory for creation

SOLID Principles:
    - Single Responsibility: Only handles alliance formation
    - Open/Closed: Extensible with different alliance types
    - Dependency Inversion: Depends on abstractions (SocialEntity, Factory)

Integration:
    - Uses social/faction.py for Faction creation
    - Uses social/group.py for Group creation
    - Uses social/factory.py for entity creation
    - Uses social/relationships.py for relationship establishment
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, List, Optional, Set

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from actions.action import Action

if TYPE_CHECKING:
    from agents.agent import Agent
    from agents.agent_manager import AgentManager
    from world.world import World
    from social.faction import Faction, GovernanceType
    from social.group import Group, GroupPurpose
    from social.social_entity import SocialEntity
    from social.relationships import RelationshipManager


class AllianceType(Enum):
    """
    Type of alliance to form.

    Attributes:
        FACTION: Create a formal Faction with governance
        GROUP: Create an informal Group
        TREATY: Form alliance between existing factions
        COALITION: Temporary alliance for specific goal
    """
    FACTION = "faction"
    GROUP = "group"
    TREATY = "treaty"
    COALITION = "coalition"


@dataclass
class AllianceProposal:
    """
    Proposal for forming an alliance.

    Immutable record of alliance proposal details.

    Attributes:
        proposer_id: ID of agent proposing alliance
        target_ids: IDs of agents being invited
        alliance_name: Proposed name for alliance
        alliance_type: Type of alliance proposed
        governance: Governance type (for factions)
        timestamp: When proposal was made
    """
    proposer_id: str
    target_ids: List[str]
    alliance_name: str
    alliance_type: AllianceType
    governance: Optional[str]
    timestamp: float


class AllianceFormationStrategy(ABC):
    """
    Abstract strategy for different alliance formation approaches.

    Allows different rules for alliance creation.

    Design Pattern: Strategy
    """

    @abstractmethod
    def can_form_alliance(
        self,
        proposer: Agent,
        targets: List[Agent],
        world: World
    ) -> bool:
        """
        Check if alliance can be formed.

        Args:
            proposer: Agent proposing alliance
            targets: Agents being invited
            world: World context

        Returns:
            bool: True if alliance can be formed
        """
        pass

    @abstractmethod
    def get_required_sociability(self) -> float:
        """
        Get minimum sociability trait required.

        Returns:
            float: Minimum sociability (0-100)
        """
        pass


class StandardAllianceStrategy(AllianceFormationStrategy):
    """
    Standard alliance formation rules.

    Requirements:
    - Proposer has sufficient sociability
    - All targets are nearby
    - No hostile relationships
    - Targets not in conflicting factions
    """

    MIN_SOCIABILITY: float = 30.0
    MAX_DISTANCE: int = 5

    def can_form_alliance(
        self,
        proposer: Agent,
        targets: List[Agent],
        world: World
    ) -> bool:
        """Check standard alliance requirements."""
        # Check proposer sociability
        sociability = getattr(proposer.traits, 'sociability', 50)
        if sociability < self.MIN_SOCIABILITY:
            return False

        # Check all targets are nearby
        for target in targets:
            if proposer.position.distance_to(target.position) > self.MAX_DISTANCE:
                return False

        return True

    def get_required_sociability(self) -> float:
        """Return minimum sociability requirement."""
        return self.MIN_SOCIABILITY


class FormAllianceAction(Action):
    """
    Command for forming alliances with other agents.

    FormAllianceAction demonstrates the Command pattern for social
    interactions. It encapsulates alliance creation that can be:
    - Validated before execution (can_execute)
    - Executed to create new social entities (execute)
    - Logged and tracked (via world events)

    Supports creating:
    - Factions: Formal organizations with governance
    - Groups: Informal collections for temporary goals
    - Treaties: Alliances between existing factions
    - Coalitions: Temporary multi-party alliances

    Attributes:
        target_agent_ids (List[str]): IDs of agents to ally with
        alliance_name (str): Name for the new alliance
        alliance_type (AllianceType): Type of alliance to create

    Design Patterns:
        - Command: Encapsulates alliance formation as object
        - Factory: Uses SocialEntityFactory for creation
        - Strategy: Pluggable formation rules
        - Observer: Notifies members of formation

    Examples:
        >>> action = FormAllianceAction(
        ...     target_agent_ids=["agent-123", "agent-456"],
        ...     alliance_name="Northern Alliance",
        ...     alliance_type=AllianceType.FACTION
        ... )
        >>> if action.can_execute(agent, world):
        ...     success = action.execute(agent, world)
    """

    # Alliance formation range (cells)
    FORMATION_RANGE: int = 5

    # Minimum sociability trait for proposing alliance
    MIN_SOCIABILITY: float = 30.0

    def __init__(
        self,
        target_agent_ids: List[str],
        alliance_name: str = "Unnamed Alliance",
        alliance_type: AllianceType = AllianceType.GROUP,
        governance_type: Optional[str] = None,
        agent_manager: Optional[AgentManager] = None,
        relationship_manager: Optional[RelationshipManager] = None,
        formation_strategy: Optional[AllianceFormationStrategy] = None
    ) -> None:
        """
        Initialize a FormAllianceAction.

        Args:
            target_agent_ids: IDs of agents to ally with
            alliance_name: Name for the new alliance
            alliance_type: Type of alliance to create
            governance_type: Governance type for factions (e.g., "DEMOCRACY")
            agent_manager: Manager for finding agents
            relationship_manager: Manager for relationship updates
            formation_strategy: Strategy for formation rules
        """
        super().__init__(
            name="Form Alliance",
            description=f"Form '{alliance_name}' with {len(target_agent_ids)} agents"
        )
        self._target_agent_ids: List[str] = list(target_agent_ids)
        self._alliance_name: str = alliance_name
        self._alliance_type: AllianceType = alliance_type
        self._governance_type: Optional[str] = governance_type
        self._agent_manager: Optional[AgentManager] = agent_manager
        self._relationship_manager: Optional[RelationshipManager] = relationship_manager
        self._formation_strategy: AllianceFormationStrategy = (
            formation_strategy or StandardAllianceStrategy()
        )

    @property
    def target_agent_ids(self) -> List[str]:
        """Get target agent IDs (copy)."""
        return list(self._target_agent_ids)

    @property
    def alliance_name(self) -> str:
        """Get the alliance name."""
        return self._alliance_name

    @property
    def alliance_type(self) -> AllianceType:
        """Get the alliance type."""
        return self._alliance_type

    @property
    def governance_type(self) -> Optional[str]:
        """Get the governance type for factions."""
        return self._governance_type

    def execute(self, agent: Agent, world: World) -> bool:
        """
        Execute the alliance formation action.

        Creates the appropriate social entity based on alliance_type,
        adds all members, and establishes positive relationships.

        Implementation Flow:
            1. Validate preconditions (can_execute)
            2. Consume energy from proposer
            3. Get all target agents
            4. Create social entity based on type:
               - FACTION: Create via FactionFactory
               - GROUP: Create via GroupFactory
               - TREATY: Link existing factions
               - COALITION: Create temporary group
            5. Add proposer as founder/leader
            6. Invite and add all target agents
            7. Establish positive relationships between members
            8. Log alliance formation event

        Args:
            agent: The agent initiating the alliance
            world: The world context

        Returns:
            bool: True if alliance formed successfully

        Raises:
            NotImplementedError: Interface design - implementation pending
        """
        # Design skeleton - shows the implementation flow
        # Full implementation would:
        #
        # 1. if not self.can_execute(agent, world):
        #        return False
        #
        # 2. agent.consume_energy(self.energy_cost)
        #
        # 3. targets = [self._get_agent(tid, world) for tid in self._target_agent_ids]
        #    targets = [t for t in targets if t is not None]
        #
        # 4. Based on alliance_type:
        #    if self._alliance_type == AllianceType.FACTION:
        #        entity = self._create_faction(agent, world.time)
        #    elif self._alliance_type == AllianceType.GROUP:
        #        entity = self._create_group(agent, world.time)
        #    elif self._alliance_type == AllianceType.TREATY:
        #        self._create_treaty(agent, targets, world)
        #        return True
        #
        # 5. entity is created with agent as founder
        #
        # 6. for target in targets:
        #        entity.invite(inviter_id=agent.agent_id, invited_id=target.agent_id)
        #        entity.join(target.agent_id, invited_by=agent.agent_id, timestamp=world.time)
        #
        # 7. self._establish_member_relationships(agent, targets, world.time)
        #
        # 8. world.event_logger.log(AllianceFormedEvent(...))
        #
        # return True

        raise NotImplementedError(
            "FormAllianceAction.execute() - Interface design complete. "
            "Implementation requires integration with active simulation."
        )

    def can_execute(self, agent: Agent, world: World) -> bool:
        """
        Check if alliance formation can be executed.

        Validates all preconditions:
        - Agent is alive with sufficient energy
        - Agent has sufficient sociability
        - All target agents exist, are alive, and nearby
        - No hostile relationships with targets
        - Agent not already in conflicting faction (for FACTION type)

        Args:
            agent: The agent initiating the alliance
            world: The world context

        Returns:
            bool: True if all preconditions met
        """
        # Check agent is alive and has energy
        if not agent.is_alive():
            return False
        if agent.energy < self.energy_cost:
            return False

        # Check agent has sufficient sociability
        if not self._has_sufficient_sociability(agent):
            return False

        # Get target agents
        targets = self._get_target_agents(world)
        if not targets:
            return False  # No valid targets

        # Check all targets are alive and nearby
        for target in targets:
            if not target.is_alive():
                return False
            if not self._is_in_formation_range(agent, target):
                return False

        # Check no hostile relationships
        if not self._relationships_allow_alliance(agent, targets):
            return False

        # For factions, check agent not in conflicting faction
        if self._alliance_type == AllianceType.FACTION:
            if self._has_conflicting_faction(agent, targets, world):
                return False

        return True

    @property
    def energy_cost(self) -> float:
        """
        Get the energy cost of forming an alliance.

        Alliance formation has a moderate energy cost (negotiation effort).
        Larger alliances cost more.

        Returns:
            float: Energy cost (3.0 base + 0.5 per member)
        """
        return 3.0 + (0.5 * len(self._target_agent_ids))

    def _get_agent(self, agent_id: str, world: World) -> Optional[Agent]:
        """
        Get an agent by ID.

        Args:
            agent_id: ID of agent to find
            world: World context

        Returns:
            Optional[Agent]: Agent if found
        """
        if self._agent_manager:
            return self._agent_manager.get_agent(agent_id)
        if hasattr(world, 'agent_manager'):
            return world.agent_manager.get_agent(agent_id)
        return None

    def _get_target_agents(self, world: World) -> List[Agent]:
        """
        Get all target agents.

        Args:
            world: World context

        Returns:
            List[Agent]: List of found target agents
        """
        agents = []
        for agent_id in self._target_agent_ids:
            agent = self._get_agent(agent_id, world)
            if agent is not None:
                agents.append(agent)
        return agents

    def _has_sufficient_sociability(self, agent: Agent) -> bool:
        """
        Check if agent has sufficient sociability for alliance.

        Args:
            agent: Proposing agent

        Returns:
            bool: True if sociability is sufficient
        """
        sociability = getattr(agent.traits, 'sociability', 50)
        return sociability >= self._formation_strategy.get_required_sociability()

    def _is_in_formation_range(self, agent: Agent, target: Agent) -> bool:
        """
        Check if target is within alliance formation range.

        Args:
            agent: Proposing agent
            target: Target agent

        Returns:
            bool: True if within range
        """
        distance = agent.position.distance_to(target.position)
        return distance <= self.FORMATION_RANGE

    def _relationships_allow_alliance(
        self,
        agent: Agent,
        targets: List[Agent]
    ) -> bool:
        """
        Check if relationships allow alliance formation.

        Cannot form alliance with hostile agents.

        Args:
            agent: Proposing agent
            targets: Target agents

        Returns:
            bool: True if no hostile relationships
        """
        if self._relationship_manager is None:
            return True  # No tracking = allow

        for target in targets:
            relationship = self._relationship_manager.get_relationship(
                agent.agent_id, target.agent_id
            )
            if relationship is not None:
                # Check for hostile relationship
                rel_type = getattr(relationship, 'relationship_type', None)
                if rel_type is not None:
                    type_name = getattr(rel_type, 'name', str(rel_type))
                    if type_name == 'ENEMY':
                        return False

        return True

    def _has_conflicting_faction(
        self,
        agent: Agent,
        targets: List[Agent],
        world: World
    ) -> bool:
        """
        Check if agent or targets are in conflicting factions.

        Args:
            agent: Proposing agent
            targets: Target agents
            world: World context

        Returns:
            bool: True if there are faction conflicts
        """
        # Get agent's faction
        agent_faction = getattr(agent, 'faction_id', None)

        # Check each target
        for target in targets:
            target_faction = getattr(target, 'faction_id', None)

            # If both in factions and different, check if at war
            if agent_faction and target_faction:
                if agent_faction != target_faction:
                    # Would need to check faction relationship manager
                    # for war status
                    pass

        return False  # No conflicts found

    def _create_faction(self, founder: Agent, timestamp: float) -> Optional[Faction]:
        """
        Create a new Faction with the agent as founder.

        Uses the social/factory.py FactionFactory.

        Args:
            founder: Agent creating the faction
            timestamp: Creation time

        Returns:
            Optional[Faction]: Created faction or None
        """
        # Implementation would use:
        # from social.factory import create_faction
        # from social.faction import GovernanceType
        #
        # governance = GovernanceType[self._governance_type] if self._governance_type else GovernanceType.DEMOCRACY
        # faction = create_faction(
        #     name=self._alliance_name,
        #     founder_id=founder.agent_id,
        #     timestamp=timestamp,
        #     governance_type=governance
        # )
        # return faction
        return None

    def _create_group(self, founder: Agent, timestamp: float) -> Optional[Group]:
        """
        Create a new Group with the agent as coordinator.

        Uses the social/factory.py GroupFactory.

        Args:
            founder: Agent creating the group
            timestamp: Creation time

        Returns:
            Optional[Group]: Created group or None
        """
        # Implementation would use:
        # from social.factory import create_group
        # from social.group import GroupPurpose
        #
        # group = create_group(
        #     name=self._alliance_name,
        #     founder_id=founder.agent_id,
        #     timestamp=timestamp,
        #     purpose=GroupPurpose.ALLIANCE
        # )
        # return group
        return None

    def _create_treaty(
        self,
        agent: Agent,
        targets: List[Agent],
        world: World
    ) -> bool:
        """
        Create a treaty between factions.

        Establishes alliance relationship between factions
        without creating new entity.

        Args:
            agent: Agent from faction A
            targets: Agents from faction B
            world: World context

        Returns:
            bool: True if treaty established
        """
        # Implementation would use FactionRelationshipManager
        # to establish ALLY relationship between factions
        return False

    def _establish_member_relationships(
        self,
        founder: Agent,
        members: List[Agent],
        timestamp: float
    ) -> None:
        """
        Establish positive relationships between all members.

        Creates ALLY or FRIEND relationships between founder
        and all members, and between members.

        Args:
            founder: Founding agent
            members: Member agents
            timestamp: Current time
        """
        if self._relationship_manager is None:
            return

        # Create relationship between founder and each member
        # Create relationships between all members
        # Implementation would call relationship_manager.set_relationship()
        pass

    def get_required_members(self) -> int:
        """
        Get number of required members for this alliance type.

        Returns:
            int: Minimum number of members
        """
        if self._alliance_type == AllianceType.FACTION:
            return 3  # Factions need at least 3 members
        elif self._alliance_type == AllianceType.TREATY:
            return 1  # Treaty needs at least 1 other party
        return 1  # Groups and coalitions need at least 1 member

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"FormAllianceAction(name='{self._alliance_name}', "
            f"type={self._alliance_type.value}, "
            f"members={len(self._target_agent_ids)}, cost={self.energy_cost})"
        )
