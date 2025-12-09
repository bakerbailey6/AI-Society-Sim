"""Tests for simulation analytics.

This module tests the analytics system including:
- StepStatistics
- AgentStatistics
- AnalyticsCollector
- Wealth/Faction/Survival analyzers
"""
import pytest
import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src')
sys.path.insert(0, src_path)

from simulation.analytics import (
    StepStatistics,
    AgentStatistics,
    FactionStatistics,
    AnalyticsCollector,
    AnalyticsObserver,
    WealthDistributionAnalyzer,
    FactionAnalyzer,
    SurvivalAnalyzer,
)


class MockAgent:
    """Mock agent for analytics testing."""

    def __init__(self, agent_id: str, name: str = "TestAgent",
                 health: float = 100.0, energy: float = 100.0):
        self.agent_id = agent_id
        self.name = name
        self.health = health
        self.max_health = 100.0
        self.energy = energy
        self.max_energy = 100.0


class MockAnalyticsObserver(AnalyticsObserver):
    """Mock observer for testing."""

    def __init__(self):
        self.step_stats = []
        self.summaries = []

    def on_step_complete(self, stats: StepStatistics) -> None:
        self.step_stats.append(stats)

    def on_simulation_complete(self, summary: dict) -> None:
        self.summaries.append(summary)


class TestStepStatistics:
    """Tests for StepStatistics dataclass."""

    def test_average_health(self):
        """Test average health calculation."""
        stats = StepStatistics(
            step_number=1,
            timestamp=0.0,
            agent_count=4,
            total_health=200.0
        )
        assert stats.average_health == 50.0

    def test_average_health_zero_agents(self):
        """Test average health with no agents."""
        stats = StepStatistics(
            step_number=1,
            timestamp=0.0,
            agent_count=0,
            total_health=0.0
        )
        assert stats.average_health == 0.0

    def test_average_energy(self):
        """Test average energy calculation."""
        stats = StepStatistics(
            step_number=1,
            timestamp=0.0,
            agent_count=5,
            total_energy=250.0
        )
        assert stats.average_energy == 50.0


class TestAgentStatistics:
    """Tests for AgentStatistics dataclass."""

    def test_is_alive(self):
        """Test alive status."""
        alive_agent = AgentStatistics(agent_id="a1", name="Agent1")
        dead_agent = AgentStatistics(agent_id="a2", name="Agent2", death_step=10)

        assert alive_agent.is_alive is True
        assert dead_agent.is_alive is False

    def test_lifespan(self):
        """Test lifespan calculation."""
        agent = AgentStatistics(
            agent_id="a1",
            name="Agent1",
            birth_step=5,
            death_step=15
        )
        assert agent.lifespan == 10

    def test_lifespan_alive(self):
        """Test lifespan returns None for alive agent."""
        agent = AgentStatistics(agent_id="a1", name="Agent1")
        assert agent.lifespan is None


class TestFactionStatistics:
    """Tests for FactionStatistics dataclass."""

    def test_is_active(self):
        """Test active status."""
        active = FactionStatistics(faction_id="f1", name="Faction1")
        dissolved = FactionStatistics(faction_id="f2", name="Faction2", dissolution_step=10)

        assert active.is_active is True
        assert dissolved.is_active is False


class TestAnalyticsCollector:
    """Tests for AnalyticsCollector."""

    def test_initialization(self):
        """Test initialization."""
        collector = AnalyticsCollector()
        assert collector is not None

    def test_record_step(self):
        """Test recording step statistics."""
        collector = AnalyticsCollector()
        agents = [MockAgent(f"agent{i}") for i in range(3)]

        stats = collector.record_step(1, agents, None)

        assert stats.step_number == 1
        assert stats.agent_count == 3
        assert stats.total_health == 300.0

    def test_record_multiple_steps(self):
        """Test recording multiple steps."""
        collector = AnalyticsCollector()
        agents = [MockAgent(f"agent{i}") for i in range(3)]

        for i in range(5):
            collector.record_step(i + 1, agents, None)

        recent = collector.get_recent_stats(3)
        assert len(recent) == 3
        assert recent[-1].step_number == 5

    def test_record_step_with_events(self):
        """Test recording step with events."""
        collector = AnalyticsCollector()
        agents = [MockAgent("agent1")]

        events = {"births": 1, "deaths": 0, "trades": 2}
        stats = collector.record_step(1, agents, None, events)

        assert stats.births == 1
        assert stats.trades == 2

    def test_observer_notification(self):
        """Test observer receives step notifications."""
        collector = AnalyticsCollector()
        observer = MockAnalyticsObserver()
        collector.add_observer(observer)

        agents = [MockAgent("agent1")]
        collector.record_step(1, agents, None)

        assert len(observer.step_stats) == 1

    def test_remove_observer(self):
        """Test removing observer."""
        collector = AnalyticsCollector()
        observer = MockAnalyticsObserver()
        collector.add_observer(observer)
        collector.remove_observer(observer)

        agents = [MockAgent("agent1")]
        collector.record_step(1, agents, None)

        assert len(observer.step_stats) == 0

    def test_record_agent_death(self):
        """Test recording agent death."""
        collector = AnalyticsCollector()
        agents = [MockAgent("agent1")]
        collector.record_step(1, agents, None)

        collector.record_agent_death("agent1", step_number=5)

        stats = collector.get_agent_stats("agent1")
        assert stats is not None
        assert stats.death_step == 5

    def test_record_faction_formed(self):
        """Test recording faction formation."""
        collector = AnalyticsCollector()
        collector.record_faction_formed("faction1", "TestFaction", step_number=3)

        stats = collector.get_faction_stats("faction1")
        assert stats is not None
        assert stats.name == "TestFaction"
        assert stats.formation_step == 3

    def test_record_faction_dissolved(self):
        """Test recording faction dissolution."""
        collector = AnalyticsCollector()
        collector.record_faction_formed("faction1", "TestFaction", step_number=3)
        collector.record_faction_dissolved("faction1", step_number=10)

        stats = collector.get_faction_stats("faction1")
        assert stats.dissolution_step == 10

    def test_get_summary(self):
        """Test getting simulation summary."""
        collector = AnalyticsCollector()
        agents = [MockAgent(f"agent{i}") for i in range(3)]

        for i in range(10):
            collector.record_step(i + 1, agents, None)

        summary = collector.get_summary()

        assert summary["total_steps"] == 10
        assert summary["unique_agents"] == 3
        assert "average_health" in summary

    def test_history_limit(self):
        """Test history respects limit."""
        collector = AnalyticsCollector(history_limit=5)
        agents = [MockAgent("agent1")]

        for i in range(10):
            collector.record_step(i + 1, agents, None)

        recent = collector.get_recent_stats(10)
        assert len(recent) == 5

    def test_clear(self):
        """Test clearing collected data."""
        collector = AnalyticsCollector()
        agents = [MockAgent("agent1")]
        collector.record_step(1, agents, None)

        collector.clear()

        summary = collector.get_summary()
        assert "error" in summary


class TestWealthDistributionAnalyzer:
    """Tests for WealthDistributionAnalyzer."""

    def test_calculate_gini_equal(self):
        """Test Gini coefficient for equal distribution."""
        analyzer = WealthDistributionAnalyzer()

        # All equal -> Gini = 0
        values = [100.0, 100.0, 100.0, 100.0]
        gini = analyzer.calculate_gini(values)

        assert gini == pytest.approx(0.0, abs=0.01)

    def test_calculate_gini_unequal(self):
        """Test Gini coefficient for unequal distribution."""
        analyzer = WealthDistributionAnalyzer()

        # Very unequal -> high Gini
        values = [1.0, 1.0, 1.0, 1000.0]
        gini = analyzer.calculate_gini(values)

        assert gini > 0.5

    def test_calculate_gini_empty(self):
        """Test Gini for empty list."""
        analyzer = WealthDistributionAnalyzer()
        gini = analyzer.calculate_gini([])
        assert gini == 0.0

    def test_calculate_gini_single(self):
        """Test Gini for single value."""
        analyzer = WealthDistributionAnalyzer()
        gini = analyzer.calculate_gini([100.0])
        assert gini == 0.0

    def test_get_wealth_percentiles(self):
        """Test percentile calculation."""
        analyzer = WealthDistributionAnalyzer()

        values = list(range(0, 100))  # 0 to 99
        percentiles = analyzer.get_wealth_percentiles(values)

        assert 10 in percentiles
        assert 50 in percentiles
        assert 90 in percentiles
        # Median should be around 50
        assert 40 <= percentiles[50] <= 60

    def test_get_distribution_summary(self):
        """Test distribution summary."""
        analyzer = WealthDistributionAnalyzer()

        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        summary = analyzer.get_distribution_summary(values)

        assert summary["count"] == 5
        assert summary["total"] == 150.0
        assert summary["mean"] == 30.0
        assert summary["median"] == 30.0
        assert summary["min"] == 10.0
        assert summary["max"] == 50.0


class TestFactionAnalyzer:
    """Tests for FactionAnalyzer."""

    def test_analyze_faction_health(self):
        """Test faction health analysis."""
        analyzer = FactionAnalyzer()

        members = [
            MockAgent("a1", health=100.0),
            MockAgent("a2", health=50.0),
            MockAgent("a3", health=10.0),
        ]

        metrics = analyzer.analyze_faction_health(members)

        assert metrics["member_count"] == 3
        assert metrics["total_health"] == 160.0
        assert metrics["average_health"] == pytest.approx(53.33, rel=0.01)
        assert metrics["min_health"] == 10.0
        assert metrics["critical_members"] == 1  # Health < 20

    def test_analyze_faction_health_empty(self):
        """Test faction health with no members."""
        analyzer = FactionAnalyzer()
        metrics = analyzer.analyze_faction_health([])
        assert "error" in metrics


class TestSurvivalAnalyzer:
    """Tests for SurvivalAnalyzer."""

    def test_get_survival_rate(self):
        """Test survival rate calculation."""
        analyzer = SurvivalAnalyzer()

        agent_stats = {
            "a1": AgentStatistics(agent_id="a1", name="Agent1"),
            "a2": AgentStatistics(agent_id="a2", name="Agent2", death_step=5),
            "a3": AgentStatistics(agent_id="a3", name="Agent3"),
            "a4": AgentStatistics(agent_id="a4", name="Agent4", death_step=3),
        }

        rate = analyzer.get_survival_rate(agent_stats)
        assert rate == 0.5  # 2/4 alive

    def test_get_survival_rate_empty(self):
        """Test survival rate with no agents."""
        analyzer = SurvivalAnalyzer()
        rate = analyzer.get_survival_rate({})
        assert rate == 0.0

    def test_analyze_lifespans(self):
        """Test lifespan analysis."""
        analyzer = SurvivalAnalyzer()

        agent_stats = {
            "a1": AgentStatistics(agent_id="a1", name="Agent1", birth_step=0, death_step=10),
            "a2": AgentStatistics(agent_id="a2", name="Agent2", birth_step=5, death_step=15),
            "a3": AgentStatistics(agent_id="a3", name="Agent3", birth_step=0, death_step=30),
        }

        analysis = analyzer.analyze_lifespans(agent_stats)

        assert analysis["sample_size"] == 3
        assert analysis["mean_lifespan"] == pytest.approx(16.67, rel=0.01)
        assert analysis["min_lifespan"] == 10
        assert analysis["max_lifespan"] == 30

    def test_get_mortality_by_step(self):
        """Test mortality tracking by step."""
        analyzer = SurvivalAnalyzer()

        agent_stats = {
            "a1": AgentStatistics(agent_id="a1", name="Agent1", death_step=5),
            "a2": AgentStatistics(agent_id="a2", name="Agent2", death_step=5),
            "a3": AgentStatistics(agent_id="a3", name="Agent3", death_step=10),
            "a4": AgentStatistics(agent_id="a4", name="Agent4"),  # Alive
        }

        mortality = analyzer.get_mortality_by_step(agent_stats)

        assert mortality[5] == 2  # Two deaths at step 5
        assert mortality[10] == 1  # One death at step 10
