"""
LearningAgent Module - Reinforcement Learning Agent

This module provides an agent that uses Q-learning (reinforcement learning)
to improve its behavior over time through experience.

Design Patterns:
    - Strategy Pattern: Learning policy is configurable
    - Memento Pattern: Q-table can be saved/restored
    - Template Method: Inherits sense-decide-act lifecycle

SOLID Principles:
    - Single Responsibility: Manages learning and decision-making
    - Open/Closed: Learning algorithm can be extended
    - Liskov Substitution: Can be used anywhere Agent is expected

Integration:
    - Uses all Action classes for action space
    - Uses World for state observation
    - Uses agent traits for state encoding
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Tuple, Any, List, TYPE_CHECKING
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import Agent
from traits import AgentTraits
from world.position import Position

if TYPE_CHECKING:
    from world.world import World
    from actions.action import Action


class StateLevel(Enum):
    """Discrete levels for state encoding."""
    CRITICAL = "critical"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class EncodedState:
    """
    Encoded state representation for Q-table.

    Hashable representation of the agent's perception
    suitable for use as Q-table keys.

    Attributes:
        energy_level: Discretized energy level
        health_level: Discretized health level
        has_resources_nearby: Whether resources are accessible
        has_enemies_nearby: Whether enemies are nearby
        has_allies_nearby: Whether allies are nearby
        terrain_type: Current terrain type string
    """
    energy_level: StateLevel
    health_level: StateLevel
    has_resources_nearby: bool
    has_enemies_nearby: bool
    has_allies_nearby: bool
    terrain_type: str

    def __hash__(self) -> int:
        """Make state hashable for Q-table."""
        return hash((
            self.energy_level,
            self.health_level,
            self.has_resources_nearby,
            self.has_enemies_nearby,
            self.has_allies_nearby,
            self.terrain_type
        ))


class StateEncoder:
    """
    Encodes world state for Q-table keys.

    Converts continuous sensor data into discrete, hashable
    state representations suitable for Q-learning.

    Design Pattern: Strategy (interchangeable encoding methods)
    """

    # Thresholds for discretizing values
    CRITICAL_THRESHOLD: float = 15.0
    LOW_THRESHOLD: float = 30.0
    MEDIUM_THRESHOLD: float = 70.0

    @classmethod
    def encode_state(cls, sensor_data: Any, agent: Agent) -> EncodedState:
        """
        Encode current state as hashable object.

        Discretizes continuous values into categorical levels
        for efficient Q-table storage.

        Args:
            sensor_data: Dict containing perception info
            agent: The learning agent

        Returns:
            EncodedState: Hashable state representation
        """
        # Discretize energy level
        energy_percent = (agent.energy / agent.max_energy) * 100 if agent.max_energy > 0 else 0
        energy_level = cls._discretize_level(energy_percent)

        # Discretize health level
        health_percent = (agent.health / agent.max_health) * 100 if agent.max_health > 0 else 0
        health_level = cls._discretize_level(health_percent)

        # Check for nearby entities
        nearby_resources = sensor_data.get('nearby_resources', [])
        nearby_agents = sensor_data.get('nearby_agents', [])
        enemies = set(sensor_data.get('enemies', []))
        allies = set(sensor_data.get('allies', []))

        has_enemies = any(
            (a[0] if isinstance(a, tuple) else a.agent_id) in enemies
            for a in nearby_agents
        )
        has_allies = any(
            (a[0] if isinstance(a, tuple) else a.agent_id) in allies
            for a in nearby_agents
        )

        # Get terrain type
        current_cell = sensor_data.get('current_cell')
        terrain_type = str(current_cell.terrain.terrain_type.name) if current_cell else "unknown"

        return EncodedState(
            energy_level=energy_level,
            health_level=health_level,
            has_resources_nearby=len(nearby_resources) > 0,
            has_enemies_nearby=has_enemies,
            has_allies_nearby=has_allies,
            terrain_type=terrain_type
        )

    @classmethod
    def _discretize_level(cls, percent: float) -> StateLevel:
        """Convert percentage to discrete level."""
        if percent < cls.CRITICAL_THRESHOLD:
            return StateLevel.CRITICAL
        elif percent < cls.LOW_THRESHOLD:
            return StateLevel.LOW
        elif percent < cls.MEDIUM_THRESHOLD:
            return StateLevel.MEDIUM
        else:
            return StateLevel.HIGH

    @staticmethod
    def get_available_actions(sensor_data: Any, agent: Agent) -> List[str]:
        """
        Get list of available action identifiers.

        Returns action names that can be taken in current state.

        Args:
            sensor_data: Perception data
            agent: The learning agent

        Returns:
            List[str]: Available action identifiers
        """
        actions = ["rest"]  # Always available

        # Check if can gather
        nearby_resources = sensor_data.get('nearby_resources', [])
        if nearby_resources:
            actions.append("gather")

        # Check if can move (4 directions)
        actions.extend(["move_north", "move_south", "move_east", "move_west"])

        # Check if can trade
        nearby_agents = sensor_data.get('nearby_agents', [])
        allies = set(sensor_data.get('allies', []))
        if any((a[0] if isinstance(a, tuple) else a.agent_id) in allies for a in nearby_agents):
            actions.append("trade")

        # Check if can attack
        enemies = set(sensor_data.get('enemies', []))
        if any((a[0] if isinstance(a, tuple) else a.agent_id) in enemies for a in nearby_agents):
            actions.append("attack")

        return actions


class RewardCalculator:
    """
    Calculates rewards for Q-learning updates.

    Provides consistent reward signals for different outcomes.

    Design Pattern: Strategy (interchangeable reward schemes)
    """

    # Reward values
    GATHER_REWARD: float = 10.0
    HEALTH_INCREASE_REWARD: float = 5.0
    ENERGY_INCREASE_REWARD: float = 3.0
    DAMAGE_PENALTY: float = -5.0
    DEATH_PENALTY: float = -100.0
    TRADE_SUCCESS_REWARD: float = 15.0
    COMBAT_VICTORY_REWARD: float = 20.0
    COMBAT_DEFEAT_PENALTY: float = -15.0
    MOVE_COST: float = -1.0

    @classmethod
    def calculate_reward(
        cls,
        pre_state: Dict[str, float],
        post_state: Dict[str, float],
        action_type: str
    ) -> float:
        """
        Calculate reward based on state change.

        Compares pre and post action states to determine reward.

        Args:
            pre_state: State before action {health, energy, resources}
            post_state: State after action {health, energy, resources}
            action_type: Type of action taken

        Returns:
            float: Reward value
        """
        reward = 0.0

        # Check for death
        if post_state.get('health', 0) <= 0:
            return cls.DEATH_PENALTY

        # Health change
        health_diff = post_state.get('health', 0) - pre_state.get('health', 0)
        if health_diff > 0:
            reward += cls.HEALTH_INCREASE_REWARD
        elif health_diff < 0:
            reward += cls.DAMAGE_PENALTY

        # Energy change (from eating food)
        energy_diff = post_state.get('energy', 0) - pre_state.get('energy', 0)
        if energy_diff > 0:
            reward += cls.ENERGY_INCREASE_REWARD

        # Resource gathering
        resources_diff = post_state.get('resources', 0) - pre_state.get('resources', 0)
        if resources_diff > 0:
            reward += cls.GATHER_REWARD

        # Action-specific rewards
        if action_type == "move":
            reward += cls.MOVE_COST
        elif action_type == "trade":
            reward += cls.TRADE_SUCCESS_REWARD
        elif action_type == "attack":
            # Would check combat outcome
            pass

        return reward


class LearningAgent(Agent):
    """
    Agent using Q-learning for adaptive behavior.

    LearningAgent maintains a Q-table mapping (state, action) pairs to
    expected rewards, gradually learning optimal strategies through
    trial and error using the Q-learning algorithm.

    Q-Learning Update Rule:
        Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]

    Where:
        - α (alpha) = learning_rate: How quickly to incorporate new information
        - γ (gamma) = discount_factor: Importance of future rewards
        - ε (epsilon) = epsilon: Probability of random exploration

    Attributes:
        learning_rate (float): How quickly to update Q-values (0-1)
        discount_factor (float): Importance of future rewards (0-1)
        epsilon (float): Exploration probability (0-1)
        q_table (Dict): Maps (state, action) pairs to Q-values
        last_state (Optional): Previous state for learning
        last_action (Optional): Previous action for learning
    """

    def __init__(
        self,
        name: str,
        position: Position,
        traits: AgentTraits,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon: float = 0.1
    ) -> None:
        """
        Initialize a LearningAgent.

        Args:
            name (str): Agent's name
            position (Position): Starting position
            traits (AgentTraits): Agent characteristics
            learning_rate (float): Learning rate α (0-1), default 0.1
            discount_factor (float): Discount factor γ (0-1), default 0.95
            epsilon (float): Exploration rate ε (0-1), default 0.1

        Raises:
            ValueError: If learning parameters are out of range

        Examples:
            >>> from traits import TraitGenerator
            >>> traits = TraitGenerator.scholar_traits()
            >>> agent = LearningAgent("Bob", Position(15, 15), traits,
            ...                       learning_rate=0.15, epsilon=0.2)
        """
        super().__init__(name, position, traits)

        # Validate learning parameters
        if not 0 <= learning_rate <= 1:
            raise ValueError("learning_rate must be between 0 and 1")
        if not 0 <= discount_factor <= 1:
            raise ValueError("discount_factor must be between 0 and 1")
        if not 0 <= epsilon <= 1:
            raise ValueError("epsilon must be between 0 and 1")

        # Q-learning parameters
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon

        # Q-table: (state, action) -> Q-value
        # State and Action will be defined once behavior system exists
        self.q_table: Dict[Tuple[Any, Any], float] = {}

        # Experience tracking for learning
        self.last_state: Optional[Any] = None
        self.last_action: Optional[Any] = None

    def sense(self, world: World) -> Any:
        """
        Sense the environment.

        Implementation will:
        - Gather perception data similar to BasicAgent
        - Encode state for Q-learning

        Args:
            world (World): The world instance

        Returns:
            Any: Perceived information (SensorData once behavior system exists)

        Note:
            To be implemented once behavior system exists.
        """
        raise NotImplementedError(
            "sense() will be implemented once behavior system exists"
        )

    def decide(self, sensor_data: Any) -> Optional[Any]:
        """
        Epsilon-greedy action selection.

        With probability epsilon, choose random action (explore).
        Otherwise, choose action with highest Q-value (exploit).

        Decision Process:
        1. Encode current state from sensor_data
        2. If random() < epsilon: choose random action (exploration)
        3. Else: choose action with max Q(state, action) (exploitation)

        Args:
            sensor_data (Any): Sensed information

        Returns:
            Optional[Any]: Chosen action (Action class once behavior system exists)

        Note:
            To be implemented once behavior system (State/Action encoding) exists.
        """
        raise NotImplementedError(
            "decide() will be implemented once behavior system exists"
        )

    def act(self, action: Any, world: World) -> None:
        """
        Execute action and update Q-table using Q-learning.

        Execution Process:
        1. Execute the action in the world
        2. Observe reward and new state
        3. Update Q-value using Q-learning formula
        4. Store current state/action for next update

        Args:
            action (Any): The action to execute
            world (World): The world instance

        Note:
            To be implemented once behavior system exists.
        """
        raise NotImplementedError(
            "act() will be implemented once behavior system exists"
        )

    def update_q_value(
        self,
        state: Any,
        action: Any,
        reward: float,
        next_state: Any
    ) -> None:
        """
        Q-learning update rule.

        Updates the Q-value for a state-action pair based on observed
        reward and the maximum Q-value of the next state.

        Formula:
            Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]

        Args:
            state (Any): Previous state
            action (Any): Action taken
            reward (float): Received reward
            next_state (Any): Resulting state

        Note:
            To be implemented once behavior system defines State/Action types.
        """
        raise NotImplementedError(
            "update_q_value() will be implemented once State/Action types exist"
        )

    def get_q_value(self, state: Any, action: Any) -> float:
        """
        Get Q-value for a state-action pair.

        Args:
            state (Any): State
            action (Any): Action

        Returns:
            float: Q-value (0.0 if pair not in table)

        Examples:
            >>> q_val = agent.get_q_value(state, action)
            >>> print(f"Q-value: {q_val:.2f}")
        """
        return self.q_table.get((state, action), 0.0)

    def set_q_value(self, state: Any, action: Any, value: float) -> None:
        """
        Set Q-value for a state-action pair.

        Args:
            state (Any): State
            action (Any): Action
            value (float): Q-value to set
        """
        self.q_table[(state, action)] = value

    def get_q_table_size(self) -> int:
        """
        Get the number of entries in Q-table.

        Returns:
            int: Number of state-action pairs learned
        """
        return len(self.q_table)

    def clear_q_table(self) -> None:
        """Clear the Q-table (reset all learning)."""
        self.q_table.clear()
        self.last_state = None
        self.last_action = None

    def save_q_table(self, filepath: str) -> None:
        """
        Save Q-table to JSON file.

        Args:
            filepath (str): Path to save file

        Note:
            State/Action keys must be JSON-serializable.
            May need custom encoding once State/Action types are defined.

        Examples:
            >>> agent.save_q_table("agent_q_table.json")
        """
        raise NotImplementedError(
            "save_q_table() requires JSON serialization of State/Action types"
        )

    def load_q_table(self, filepath: str) -> None:
        """
        Load Q-table from JSON file.

        Args:
            filepath (str): Path to load file

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid

        Examples:
            >>> agent.load_q_table("agent_q_table.json")
        """
        raise NotImplementedError(
            "load_q_table() requires JSON deserialization of State/Action types"
        )

    def decay_epsilon(self, decay_rate: float = 0.995) -> None:
        """
        Gradually reduce exploration rate.

        Over time, agent should explore less and exploit more.

        Args:
            decay_rate (float): Multiplicative decay factor (e.g., 0.995)

        Examples:
            >>> agent.epsilon = 0.5
            >>> agent.decay_epsilon(0.9)
            >>> print(agent.epsilon)  # Now 0.45
        """
        self.epsilon = max(0.01, self.epsilon * decay_rate)

    def __repr__(self) -> str:
        """
        String representation of LearningAgent.

        Returns:
            str: Detailed representation
        """
        return (
            f"LearningAgent("
            f"name={self.name}, "
            f"pos={self.position}, "
            f"q_table_size={len(self.q_table)}, "
            f"ε={self.epsilon:.3f})"
        )
