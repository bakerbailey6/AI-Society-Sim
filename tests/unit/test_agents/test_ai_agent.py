"""Tests for AIAgent.

This module tests the LLM-powered agent including:
- LLM provider abstraction
- Prompt building
- Response parsing
- Conversation history
"""
import pytest
import json
import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src')
sys.path.insert(0, src_path)

from world.position import Position
from agents.traits import AgentTraits
from agents.ai_agent import (
    AIAgent,
    LLMProvider,
    MockLLMProvider,
    ClaudeLLMProvider,
    PromptBuilder,
    LLMResponse,
)


@pytest.fixture
def default_traits():
    """Provide default agent traits."""
    return AgentTraits(
        strength=50,
        intelligence=50,
        sociability=50,
        aggression=50,
        curiosity=50
    )


@pytest.fixture
def ai_agent(default_traits):
    """Provide an AI agent."""
    return AIAgent(
        name="Claude",
        position=Position(5, 5),
        traits=default_traits,
        model="mock-1.0"
    )


class TestMockLLMProvider:
    """Tests for MockLLMProvider."""

    def test_initialization(self):
        """Test mock provider initialization."""
        provider = MockLLMProvider()
        assert provider.get_model_name() == "mock-1.0"

    def test_query_low_health(self):
        """Test mock responds to low health."""
        provider = MockLLMProvider()

        response = provider.query("Agent has low health, dying", [])
        data = json.loads(response)

        assert data["action"] == "rest"

    def test_query_hungry(self):
        """Test mock responds to hunger."""
        provider = MockLLMProvider()

        response = provider.query("Agent is hungry, low energy", [])
        data = json.loads(response)

        assert data["action"] == "gather"
        assert data["parameters"]["resource"] == "food"

    def test_query_enemy(self):
        """Test mock responds to enemy."""
        provider = MockLLMProvider()

        response = provider.query("Enemy nearby, threat detected", [])
        data = json.loads(response)

        assert data["action"] == "move"
        assert "away" in str(data["parameters"]).lower()

    def test_query_resources(self):
        """Test mock responds to resources."""
        provider = MockLLMProvider()

        response = provider.query("Resource nearby, food nearby", [])
        data = json.loads(response)

        assert data["action"] == "gather"

    def test_query_ally(self):
        """Test mock responds to ally."""
        provider = MockLLMProvider()

        response = provider.query("Ally agent spotted", [])
        data = json.loads(response)

        assert data["action"] == "trade"

    def test_query_default(self):
        """Test mock default response."""
        provider = MockLLMProvider()

        response = provider.query("Nothing special happening", [])
        data = json.loads(response)

        assert data["action"] == "move"
        assert "reasoning" in data


class TestClaudeLLMProvider:
    """Tests for ClaudeLLMProvider."""

    def test_initialization(self):
        """Test Claude provider initialization."""
        provider = ClaudeLLMProvider(api_key="test-key")
        assert "claude" in provider.get_model_name()

    def test_custom_model(self):
        """Test custom model specification."""
        provider = ClaudeLLMProvider(api_key="test-key", model="claude-3-opus")
        assert provider.get_model_name() == "claude-3-opus"

    def test_query_not_implemented(self):
        """Test query raises NotImplementedError."""
        provider = ClaudeLLMProvider(api_key="test-key")

        with pytest.raises(NotImplementedError):
            provider.query("test", [])


class TestAIAgentInitialization:
    """Tests for AIAgent initialization."""

    def test_default_initialization(self, default_traits):
        """Test default initialization."""
        agent = AIAgent(
            name="Test",
            position=Position(0, 0),
            traits=default_traits
        )

        assert agent.name == "Test"
        assert "claude" in agent.model.lower()

    def test_custom_model(self, default_traits):
        """Test custom model specification."""
        agent = AIAgent(
            name="Test",
            position=Position(0, 0),
            traits=default_traits,
            model="gpt-4"
        )

        assert agent.model == "gpt-4"

    def test_api_key_from_param(self, default_traits):
        """Test API key from parameter."""
        agent = AIAgent(
            name="Test",
            position=Position(0, 0),
            traits=default_traits,
            api_key="test-key"
        )

        assert agent.api_key == "test-key"


class TestConversationHistory:
    """Tests for conversation history management."""

    def test_empty_history(self, ai_agent):
        """Test history starts empty."""
        assert len(ai_agent.conversation_history) == 0

    def test_add_to_history(self, ai_agent):
        """Test adding messages to history."""
        ai_agent.add_to_history("user", "Hello")
        ai_agent.add_to_history("assistant", "Hi there")

        assert len(ai_agent.conversation_history) == 2
        assert ai_agent.conversation_history[0]["role"] == "user"
        assert ai_agent.conversation_history[1]["role"] == "assistant"

    def test_clear_history(self, ai_agent):
        """Test clearing history."""
        ai_agent.add_to_history("user", "Test")
        ai_agent.clear_history()

        assert len(ai_agent.conversation_history) == 0

    def test_history_trimming(self, ai_agent):
        """Test history is trimmed when too long."""
        ai_agent.set_max_context_length(3)

        # Add more than max context
        for i in range(10):
            ai_agent.add_to_history("user", f"Message {i}")
            ai_agent.add_to_history("assistant", f"Response {i}")

        # Should be trimmed to max_context_length * 2
        assert len(ai_agent.conversation_history) <= 6

    def test_set_max_context_length(self, ai_agent):
        """Test setting max context length."""
        ai_agent.set_max_context_length(20)
        assert ai_agent.max_context_length == 20

    def test_invalid_max_context_length(self, ai_agent):
        """Test invalid max context length raises error."""
        with pytest.raises(ValueError):
            ai_agent.set_max_context_length(0)


class TestPromptBuilder:
    """Tests for PromptBuilder."""

    def test_format_traits(self):
        """Test trait formatting."""
        class MockTraits:
            strength = 80
            agility = 60
            intelligence = 70
            sociability = 50

        traits_str = PromptBuilder._format_traits(MockTraits())

        assert "Strength: 80" in traits_str
        assert "Intelligence: 70" in traits_str

    def test_format_available_actions_basic(self):
        """Test basic action formatting."""
        sensor_data = {'nearby_agents': []}

        actions_str = PromptBuilder._format_available_actions(sensor_data)

        assert "move" in actions_str.lower()
        assert "gather" in actions_str.lower()
        assert "rest" in actions_str.lower()

    def test_format_available_actions_with_agents(self):
        """Test actions include trade/attack with nearby agents."""
        sensor_data = {'nearby_agents': [("agent1", None, 1.0)]}

        actions_str = PromptBuilder._format_available_actions(sensor_data)

        assert "trade" in actions_str.lower()
        assert "attack" in actions_str.lower()

    def test_format_perception_no_resources(self):
        """Test perception formatting without resources."""
        sensor_data = {
            'nearby_resources': [],
            'nearby_agents': [],
            'current_cell': None
        }

        perception_str = PromptBuilder._format_perception(sensor_data)

        assert "No resources" in perception_str

    def test_format_perception_with_resources(self):
        """Test perception formatting with resources."""
        sensor_data = {
            'nearby_resources': [1, 2, 3],  # 3 resources
            'nearby_agents': [],
            'current_cell': None
        }

        perception_str = PromptBuilder._format_perception(sensor_data)

        assert "3 found" in perception_str


class TestLLMResponse:
    """Tests for LLMResponse dataclass."""

    def test_llm_response_creation(self):
        """Test LLMResponse creation."""
        response = LLMResponse(
            action="move",
            parameters={"direction": "north"},
            reasoning="Need to explore",
            raw_response='{"action": "move"}'
        )

        assert response.action == "move"
        assert response.parameters["direction"] == "north"
        assert response.reasoning == "Need to explore"


class TestAIAgentRepr:
    """Tests for string representation."""

    def test_repr(self, ai_agent):
        """Test repr includes key information."""
        repr_str = repr(ai_agent)

        assert "AIAgent" in repr_str
        assert "Claude" in repr_str
        assert "mock-1.0" in repr_str
