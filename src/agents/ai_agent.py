"""
AIAgent Module - LLM-Powered Agent

This module provides an agent powered by a Large Language Model (LLM)
for sophisticated, natural language-based decision making.

Design Patterns:
    - Strategy Pattern: LLM provider is pluggable
    - Adapter Pattern: Wraps LLM API for agent interface
    - Template Method: Inherits sense-decide-act lifecycle

SOLID Principles:
    - Single Responsibility: Manages LLM-based decision making
    - Open/Closed: Can support different LLM providers
    - Dependency Inversion: Depends on abstract LLM interface

Integration:
    - Uses all Action classes for action parsing
    - Uses World for state observation
    - Supports multiple LLM providers (Claude, GPT, Mock)

Note:
    This is an advanced optional feature requiring API access.
    May be omitted in basic implementations.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, TYPE_CHECKING
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


class LLMProvider(ABC):
    """
    Abstract interface for LLM providers.

    Allows different LLM implementations to be plugged in
    using the Strategy pattern.

    Implementations:
        - ClaudeLLMProvider: Anthropic Claude API
        - OpenAILLMProvider: OpenAI GPT API
        - MockLLMProvider: Rule-based mock for testing

    Design Pattern: Strategy
    """

    @abstractmethod
    def query(
        self,
        prompt: str,
        history: List[Dict[str, str]]
    ) -> str:
        """
        Send query to LLM and get response.

        Args:
            prompt: The prompt to send
            history: Conversation history for context

        Returns:
            str: LLM response text

        Raises:
            RuntimeError: If API call fails
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the model identifier.

        Returns:
            str: Model name/identifier
        """
        pass


class ClaudeLLMProvider(LLMProvider):
    """
    Anthropic Claude API provider.

    Requires anthropic library and valid API key.

    Attributes:
        api_key: Anthropic API key
        model: Model identifier
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022"
    ) -> None:
        """
        Initialize Claude provider.

        Args:
            api_key: Anthropic API key
            model: Model identifier
        """
        self._api_key = api_key
        self._model = model

    def query(self, prompt: str, history: List[Dict[str, str]]) -> str:
        """
        Query Claude API.

        Implementation would use anthropic library:
            client = anthropic.Anthropic(api_key=self._api_key)
            message = client.messages.create(
                model=self._model,
                max_tokens=1024,
                messages=history + [{"role": "user", "content": prompt}]
            )
            return message.content[0].text

        Raises:
            NotImplementedError: API integration pending
        """
        raise NotImplementedError(
            "ClaudeLLMProvider requires anthropic library integration"
        )

    def get_model_name(self) -> str:
        """Return model identifier."""
        return self._model


class MockLLMProvider(LLMProvider):
    """
    Mock LLM provider for testing without API.

    Returns rule-based responses for testing agent behavior
    without requiring actual API calls.

    Useful for:
        - Unit testing
        - Offline development
        - Cost-free experimentation
    """

    def __init__(self) -> None:
        """Initialize mock provider."""
        self._model = "mock-1.0"

    def query(self, prompt: str, history: List[Dict[str, str]]) -> str:
        """
        Return rule-based mock response.

        Parses prompt for keywords and returns appropriate action.

        Args:
            prompt: The prompt to analyze
            history: Ignored for mock

        Returns:
            str: JSON-formatted action response
        """
        prompt_lower = prompt.lower()

        # Analyze prompt for key indicators
        if "low health" in prompt_lower or "dying" in prompt_lower:
            action = {"action": "rest", "parameters": {}, "reasoning": "Need to recover health"}
        elif "hungry" in prompt_lower or "low energy" in prompt_lower:
            action = {"action": "gather", "parameters": {"resource": "food"}, "reasoning": "Need food for energy"}
        elif "enemy" in prompt_lower or "threat" in prompt_lower:
            action = {"action": "move", "parameters": {"direction": "away"}, "reasoning": "Avoiding danger"}
        elif "resource" in prompt_lower or "food nearby" in prompt_lower:
            action = {"action": "gather", "parameters": {}, "reasoning": "Resources available"}
        elif "ally" in prompt_lower:
            action = {"action": "trade", "parameters": {}, "reasoning": "Trading with ally"}
        else:
            action = {"action": "move", "parameters": {"direction": "random"}, "reasoning": "Exploring"}

        return json.dumps(action)

    def get_model_name(self) -> str:
        """Return mock model name."""
        return self._model


@dataclass
class LLMResponse:
    """
    Parsed response from LLM.

    Attributes:
        action: Action type string
        parameters: Action parameters
        reasoning: LLM's reasoning for the choice
        raw_response: Original LLM output
    """
    action: str
    parameters: Dict[str, Any]
    reasoning: str
    raw_response: str


class PromptBuilder:
    """
    Builds prompts for LLM agents.

    Constructs well-formatted prompts including agent state,
    perception data, available actions, and persona.

    Design Pattern: Builder
    """

    # System prompt template
    SYSTEM_TEMPLATE = """You are {agent_name}, {persona}.

Your current state:
- Health: {health}/{max_health}
- Energy: {energy}/{max_energy}
- Position: ({x}, {y})

Your traits:
{traits}

You can take the following actions:
{available_actions}

Respond with a JSON object containing:
- "action": the action type
- "parameters": any action parameters
- "reasoning": brief explanation of your choice
"""

    @classmethod
    def build_prompt(
        cls,
        agent: Any,
        sensor_data: Any,
        persona: str = "a survival-focused agent"
    ) -> str:
        """
        Build complete prompt from agent state and perception.

        Args:
            agent: The AI agent
            sensor_data: Current perception
            persona: Agent personality description

        Returns:
            str: Formatted prompt
        """
        # Format traits
        traits_str = cls._format_traits(agent.traits)

        # Format available actions
        actions_str = cls._format_available_actions(sensor_data)

        # Format perception
        perception_str = cls._format_perception(sensor_data)

        prompt = cls.SYSTEM_TEMPLATE.format(
            agent_name=agent.name,
            persona=persona,
            health=agent.health,
            max_health=agent.max_health,
            energy=agent.energy,
            max_energy=agent.max_energy,
            x=agent.position.x,
            y=agent.position.y,
            traits=traits_str,
            available_actions=actions_str
        )

        prompt += f"\n\nCurrent perception:\n{perception_str}"
        prompt += "\n\nWhat action do you take?"

        return prompt

    @staticmethod
    def _format_traits(traits: Any) -> str:
        """Format agent traits for prompt."""
        trait_lines = []
        for attr in ['strength', 'agility', 'intelligence', 'sociability']:
            value = getattr(traits, attr, 50)
            trait_lines.append(f"- {attr.capitalize()}: {value}")
        return "\n".join(trait_lines)

    @staticmethod
    def _format_available_actions(sensor_data: Any) -> str:
        """Format available actions for prompt."""
        actions = [
            "- move: Move in a direction (north, south, east, west)",
            "- gather: Gather nearby resources",
            "- rest: Rest to recover energy",
        ]

        nearby_agents = sensor_data.get('nearby_agents', [])
        if nearby_agents:
            actions.append("- trade: Trade resources with nearby agent")
            actions.append("- attack: Attack nearby enemy")

        return "\n".join(actions)

    @staticmethod
    def _format_perception(sensor_data: Any) -> str:
        """Format perception data for prompt."""
        lines = []

        # Resources
        resources = sensor_data.get('nearby_resources', [])
        if resources:
            lines.append(f"- Nearby resources: {len(resources)} found")
        else:
            lines.append("- No resources nearby")

        # Agents
        agents = sensor_data.get('nearby_agents', [])
        if agents:
            lines.append(f"- Nearby agents: {len(agents)} visible")
        else:
            lines.append("- No other agents nearby")

        # Terrain
        cell = sensor_data.get('current_cell')
        if cell:
            lines.append(f"- Current terrain: {cell.terrain.terrain_type.name}")

        return "\n".join(lines)


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
