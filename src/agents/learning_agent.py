"""
LearningAgent Module - Reinforcement Learning Agent

This module provides an agent that uses Q-learning (reinforcement learning)
to improve its behavior over time through experience.

Design Patterns:
    - Strategy Pattern: Learning policy is configurable
    - Memento Pattern: Q-table can be saved/restored

SOLID Principles:
    - Single Responsibility: Manages learning and decision-making
    - Open/Closed: Learning algorithm can be extended
    - Liskov Substitution: Can be used anywhere Agent is expected
"""

from __future__ import annotations
from typing import Optional, Dict, Tuple, Any, TYPE_CHECKING
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import Agent
from traits import AgentTraits
from world.position import Position

if TYPE_CHECKING:
    from world.world import World


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
