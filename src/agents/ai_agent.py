"""
AIAgent Module - LLM-Powered Agent

This module provides an agent powered by a Large Language Model (LLM)
for sophisticated, natural language-based decision making.

Design Patterns:
    - Strategy Pattern: LLM provider is pluggable
    - Adapter Pattern: Wraps LLM API for agent interface

SOLID Principles:
    - Single Responsibility: Manages LLM-based decision making
    - Open/Closed: Can support different LLM providers
    - Dependency Inversion: Depends on abstract LLM interface

Note:
    This is an advanced optional feature requiring API access.
    May be omitted in basic implementations.
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any, TYPE_CHECKING

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import Agent
from traits import AgentTraits
from world.position import Position

if TYPE_CHECKING:
    from world.world import World


class AIAgent(Agent):
    """
    Agent using Large Language Model for decision-making.

    AIAgent queries an LLM (e.g., Claude, GPT-4) to make context-aware,
    sophisticated decisions based on natural language reasoning.

    The agent constructs prompts from its sensory data and receives
    structured responses that are parsed into actions.

    Attributes:
        api_key (Optional[str]): API key for LLM service
        model (str): Model identifier (e.g., "claude-3-5-sonnet-20241022")
        conversation_history (List[Dict]): Message history for context
        max_context_length (int): Maximum messages to keep in history

    Note:
        This implementation requires external API access and may incur costs.
        The LLM interface will be abstracted once behavior system exists.
    """

    def __init__(
        self,
        name: str,
        position: Position,
        traits: AgentTraits,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022"
    ) -> None:
        """
        Initialize an AIAgent.

        Args:
            name (str): Agent's name
            position (Position): Starting position
            traits (AgentTraits): Agent characteristics
            api_key (Optional[str]): LLM API key (can be set via environment)
            model (str): LLM model identifier

        Examples:
            >>> from traits import TraitGenerator
            >>> traits = TraitGenerator.scholar_traits()
            >>> agent = AIAgent("Charlie", Position(20, 20), traits,
            ...                 api_key="your-api-key")
        """
        super().__init__(name, position, traits)

        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model

        # Conversation history for maintaining context
        self.conversation_history: List[Dict[str, str]] = []
        self.max_context_length = 10  # Keep last 10 exchanges

    def sense(self, world: World) -> Any:
        """
        Sense the environment.

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
        Use LLM to decide action.

        Decision Process:
        1. Construct prompt from sensor_data and agent state
        2. Query LLM with prompt
        3. Parse LLM response into structured action
        4. Return action

        Args:
            sensor_data (Any): Sensed information

        Returns:
            Optional[Any]: LLM-chosen action (Action class once behavior system exists)

        Note:
            To be implemented once:
            - Behavior system defines Action types
            - LLM API interface is implemented
        """
        raise NotImplementedError(
            "decide() will be implemented once LLM interface and Action types exist"
        )

    def act(self, action: Any, world: World) -> None:
        """
        Execute the LLM-chosen action.

        Args:
            action (Any): The action to execute
            world (World): The world instance

        Note:
            To be implemented once behavior system exists.
        """
        raise NotImplementedError(
            "act() will be implemented once behavior system exists"
        )

    def _construct_prompt(self, sensor_data: Any) -> str:
        """
        Build LLM prompt from current state and sensory data.

        The prompt includes:
        - Agent's current state (health, energy, position)
        - Sensory information (nearby resources, agents, terrain)
        - Agent's traits and personality
        - Available actions
        - Recent history

        Args:
            sensor_data (Any): Current perception

        Returns:
            str: Formatted prompt for LLM

        Note:
            To be implemented once SensorData structure exists.
        """
        raise NotImplementedError(
            "Prompt construction requires SensorData structure"
        )

    def _parse_llm_response(self, response: str) -> Optional[Any]:
        """
        Parse LLM response into an action.

        Expected response format (example):
        {
            "action_type": "move",
            "parameters": {"direction": "north"},
            "reasoning": "Need to explore north for food"
        }

        Args:
            response (str): LLM output

        Returns:
            Optional[Any]: Parsed action (Action class once behavior system exists)

        Raises:
            ValueError: If response format is invalid

        Note:
            To be implemented once Action types are defined.
        """
        raise NotImplementedError(
            "Response parsing requires Action type definitions"
        )

    def _query_llm(self, prompt: str) -> str:
        """
        Query the LLM API.

        Args:
            prompt (str): Prompt to send

        Returns:
            str: LLM response

        Raises:
            RuntimeError: If API key not set
            Exception: If API call fails

        Note:
            Requires LLM API client library (e.g., anthropic).
        """
        raise NotImplementedError(
            "LLM querying requires API client implementation"
        )

    def add_to_history(self, role: str, content: str) -> None:
        """
        Add message to conversation history.

        Args:
            role (str): Message role ("user" or "assistant")
            content (str): Message content
        """
        self.conversation_history.append({
            "role": role,
            "content": content
        })

        # Trim history if too long
        if len(self.conversation_history) > self.max_context_length * 2:
            # Keep system message and recent messages
            self.conversation_history = self.conversation_history[-self.max_context_length * 2:]

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()

    def set_max_context_length(self, length: int) -> None:
        """
        Set maximum conversation history length.

        Args:
            length (int): Maximum number of exchanges to keep
        """
        if length < 1:
            raise ValueError("max_context_length must be at least 1")
        self.max_context_length = length

    def __repr__(self) -> str:
        """
        String representation of AIAgent.

        Returns:
            str: Detailed representation
        """
        return (
            f"AIAgent("
            f"name={self.name}, "
            f"pos={self.position}, "
            f"model={self.model}, "
            f"history_length={len(self.conversation_history)})"
        )
