"""
Analytics Module

This module provides analytics collection and analysis for simulations.
Tracks statistics, detects patterns, and generates reports.

Design Patterns:
    - Observer Pattern: Collectors observe simulation events
    - Strategy Pattern: Different analyzers for different metrics
    - Visitor Pattern: Analyzers visit simulation components

SOLID Principles:
    - Single Responsibility: Each analyzer handles one type of analysis
    - Open/Closed: New analyzers can be added without modification
    - Interface Segregation: Focused analyzer interfaces

Integration:
    - Uses agents/agent.py for agent statistics
    - Uses social/faction.py for faction analysis
    - Uses economy/marketplace.py for economic analysis
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Dict, List, Optional, Any, Set
from collections import defaultdict
import statistics
import time

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if TYPE_CHECKING:
    from agents.agent import Agent
    from world.world import World
    from social.faction import Faction


class MetricType(Enum):
    """Types of metrics tracked."""
    POPULATION = auto()
    HEALTH = auto()
    ENERGY = auto()
    WEALTH = auto()
    COMBAT = auto()
    TRADE = auto()
    FACTION = auto()
    SURVIVAL = auto()


@dataclass
class StepStatistics:
    """
    Statistics for a single simulation step.

    Attributes:
        step_number: Step number
        timestamp: When step occurred
        agent_count: Number of active agents
        total_health: Sum of all agent health
        total_energy: Sum of all agent energy
        births: Agents created this step
        deaths: Agents died this step
        trades: Trades completed this step
        combats: Combat events this step
        custom_metrics: Additional custom metrics
    """
    step_number: int
    timestamp: float
    agent_count: int = 0
    total_health: float = 0.0
    total_energy: float = 0.0
    births: int = 0
    deaths: int = 0
    trades: int = 0
    combats: int = 0
    custom_metrics: Dict[str, Any] = field(default_factory=dict)

    @property
    def average_health(self) -> float:
        """Average health per agent."""
        return self.total_health / self.agent_count if self.agent_count > 0 else 0.0

    @property
    def average_energy(self) -> float:
        """Average energy per agent."""
        return self.total_energy / self.agent_count if self.agent_count > 0 else 0.0


@dataclass
class AgentStatistics:
    """
    Statistics for a single agent.

    Attributes:
        agent_id: Agent identifier
        name: Agent name
        birth_step: Step when agent was created
        death_step: Step when agent died (None if alive)
        total_actions: Actions taken
        resources_gathered: Total resources gathered
        trades_completed: Trades participated in
        combats_won: Combat victories
        combats_lost: Combat defeats
        faction_memberships: Factions joined
    """
    agent_id: str
    name: str
    birth_step: int = 0
    death_step: Optional[int] = None
    total_actions: int = 0
    resources_gathered: float = 0.0
    trades_completed: int = 0
    combats_won: int = 0
    combats_lost: int = 0
    faction_memberships: List[str] = field(default_factory=list)

    @property
    def is_alive(self) -> bool:
        """Whether agent is still alive."""
        return self.death_step is None

    @property
    def lifespan(self) -> Optional[int]:
        """Agent lifespan in steps (None if still alive)."""
        if self.death_step is not None:
            return self.death_step - self.birth_step
        return None


@dataclass
class FactionStatistics:
    """
    Statistics for a faction.

    Attributes:
        faction_id: Faction identifier
        name: Faction name
        formation_step: When faction was formed
        dissolution_step: When faction dissolved (None if active)
        peak_membership: Maximum members
        total_members_ever: All agents who joined
        trades_internal: Trades between members
        combats_external: Combats with non-members
    """
    faction_id: str
    name: str
    formation_step: int = 0
    dissolution_step: Optional[int] = None
    peak_membership: int = 0
    total_members_ever: int = 0
    trades_internal: int = 0
    combats_external: int = 0

    @property
    def is_active(self) -> bool:
        """Whether faction is still active."""
        return self.dissolution_step is None


class AnalyticsObserver(ABC):
    """
    Abstract observer for analytics events.

    Implementations receive analytics data for processing,
    storage, or visualization.

    Design Pattern: Observer
    """

    @abstractmethod
    def on_step_complete(self, stats: StepStatistics) -> None:
        """
        Called when a simulation step completes.

        Args:
            stats: Statistics for the completed step
        """
        pass

    @abstractmethod
    def on_simulation_complete(self, summary: Dict[str, Any]) -> None:
        """
        Called when simulation ends.

        Args:
            summary: Final simulation summary
        """
        pass


class AnalyticsCollector:
    """
    Main analytics collector for simulation.

    Collects statistics each step, maintains history,
    and provides summary methods.

    Design Patterns:
        - Observer: Notifies analytics observers
        - Facade: Simplifies analytics access

    Attributes:
        step_history: Historical step statistics
        agent_stats: Per-agent statistics
        faction_stats: Per-faction statistics
        observers: Analytics observers

    Examples:
        >>> collector = AnalyticsCollector()
        >>> collector.record_step(step_num, agents, world)
        >>> summary = collector.get_summary()
    """

    DEFAULT_HISTORY_LIMIT: int = 10000

    def __init__(self, history_limit: int = DEFAULT_HISTORY_LIMIT) -> None:
        """
        Initialize AnalyticsCollector.

        Args:
            history_limit: Maximum steps to retain
        """
        self._history_limit = history_limit
        self._step_history: List[StepStatistics] = []
        self._agent_stats: Dict[str, AgentStatistics] = {}
        self._faction_stats: Dict[str, FactionStatistics] = {}
        self._observers: List[AnalyticsObserver] = []

        # Tracking state
        self._current_step = 0
        self._start_time = time.time()

    def record_step(
        self,
        step_number: int,
        agents: List[Agent],
        world: World,
        events: Optional[Dict[str, Any]] = None
    ) -> StepStatistics:
        """
        Record statistics for a simulation step.

        Args:
            step_number: Current step number
            agents: Active agents
            world: World instance
            events: Optional event data (trades, combats, etc.)

        Returns:
            StepStatistics: Statistics for this step
        """
        events = events or {}

        # Calculate statistics
        stats = StepStatistics(
            step_number=step_number,
            timestamp=time.time(),
            agent_count=len(agents),
            total_health=sum(a.health for a in agents),
            total_energy=sum(a.energy for a in agents),
            births=events.get("births", 0),
            deaths=events.get("deaths", 0),
            trades=events.get("trades", 0),
            combats=events.get("combats", 0),
            custom_metrics=events.get("custom", {})
        )

        # Add to history
        self._step_history.append(stats)

        # Trim history if needed
        if len(self._step_history) > self._history_limit:
            self._step_history = self._step_history[-self._history_limit:]

        self._current_step = step_number

        # Update agent stats
        for agent in agents:
            self._update_agent_stats(agent, step_number)

        # Notify observers
        for observer in self._observers:
            try:
                observer.on_step_complete(stats)
            except Exception:
                pass

        return stats

    def _update_agent_stats(self, agent: Agent, step_number: int) -> None:
        """Update statistics for an agent."""
        agent_id = agent.agent_id

        if agent_id not in self._agent_stats:
            self._agent_stats[agent_id] = AgentStatistics(
                agent_id=agent_id,
                name=agent.name,
                birth_step=step_number
            )

    def record_agent_death(self, agent_id: str, step_number: int) -> None:
        """
        Record agent death.

        Args:
            agent_id: ID of deceased agent
            step_number: Step of death
        """
        if agent_id in self._agent_stats:
            self._agent_stats[agent_id].death_step = step_number

    def record_agent_action(self, agent_id: str, action_type: str) -> None:
        """
        Record an agent action.

        Args:
            agent_id: Agent who acted
            action_type: Type of action
        """
        if agent_id in self._agent_stats:
            self._agent_stats[agent_id].total_actions += 1

            if action_type == "gather":
                self._agent_stats[agent_id].resources_gathered += 1
            elif action_type == "trade":
                self._agent_stats[agent_id].trades_completed += 1

    def record_combat_result(
        self,
        winner_id: str,
        loser_id: str
    ) -> None:
        """
        Record combat result.

        Args:
            winner_id: Winning agent ID
            loser_id: Losing agent ID
        """
        if winner_id in self._agent_stats:
            self._agent_stats[winner_id].combats_won += 1
        if loser_id in self._agent_stats:
            self._agent_stats[loser_id].combats_lost += 1

    def record_faction_formed(
        self,
        faction_id: str,
        name: str,
        step_number: int
    ) -> None:
        """
        Record faction formation.

        Args:
            faction_id: New faction ID
            name: Faction name
            step_number: Formation step
        """
        self._faction_stats[faction_id] = FactionStatistics(
            faction_id=faction_id,
            name=name,
            formation_step=step_number
        )

    def record_faction_dissolved(
        self,
        faction_id: str,
        step_number: int
    ) -> None:
        """
        Record faction dissolution.

        Args:
            faction_id: Dissolved faction ID
            step_number: Dissolution step
        """
        if faction_id in self._faction_stats:
            self._faction_stats[faction_id].dissolution_step = step_number

    def get_step_stats(self, step_number: int) -> Optional[StepStatistics]:
        """
        Get statistics for a specific step.

        Args:
            step_number: Step to retrieve

        Returns:
            Optional[StepStatistics]: Stats or None if not found
        """
        for stats in self._step_history:
            if stats.step_number == step_number:
                return stats
        return None

    def get_recent_stats(self, count: int = 10) -> List[StepStatistics]:
        """
        Get recent step statistics.

        Args:
            count: Number of recent steps

        Returns:
            List[StepStatistics]: Recent statistics
        """
        return self._step_history[-count:]

    def get_agent_stats(self, agent_id: str) -> Optional[AgentStatistics]:
        """
        Get statistics for an agent.

        Args:
            agent_id: Agent ID

        Returns:
            Optional[AgentStatistics]: Agent stats or None
        """
        return self._agent_stats.get(agent_id)

    def get_faction_stats(self, faction_id: str) -> Optional[FactionStatistics]:
        """
        Get statistics for a faction.

        Args:
            faction_id: Faction ID

        Returns:
            Optional[FactionStatistics]: Faction stats or None
        """
        return self._faction_stats.get(faction_id)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get simulation summary.

        Returns:
            Dict: Summary statistics
        """
        if not self._step_history:
            return {"error": "No data collected"}

        total_steps = len(self._step_history)
        elapsed_time = time.time() - self._start_time

        # Calculate averages
        avg_agents = statistics.mean(s.agent_count for s in self._step_history)
        avg_health = statistics.mean(s.average_health for s in self._step_history)
        avg_energy = statistics.mean(s.average_energy for s in self._step_history)

        # Count totals
        total_births = sum(s.births for s in self._step_history)
        total_deaths = sum(s.deaths for s in self._step_history)
        total_trades = sum(s.trades for s in self._step_history)
        total_combats = sum(s.combats for s in self._step_history)

        return {
            "total_steps": total_steps,
            "elapsed_time_seconds": elapsed_time,
            "steps_per_second": total_steps / elapsed_time if elapsed_time > 0 else 0,
            "average_agent_count": avg_agents,
            "average_health": avg_health,
            "average_energy": avg_energy,
            "total_births": total_births,
            "total_deaths": total_deaths,
            "total_trades": total_trades,
            "total_combats": total_combats,
            "unique_agents": len(self._agent_stats),
            "unique_factions": len(self._faction_stats),
        }

    def add_observer(self, observer: AnalyticsObserver) -> None:
        """Add analytics observer."""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: AnalyticsObserver) -> None:
        """Remove analytics observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def clear(self) -> None:
        """Clear all collected data."""
        self._step_history.clear()
        self._agent_stats.clear()
        self._faction_stats.clear()
        self._current_step = 0
        self._start_time = time.time()


class WealthDistributionAnalyzer:
    """
    Analyzer for wealth distribution patterns.

    Calculates inequality metrics like Gini coefficient
    and wealth percentiles.

    Examples:
        >>> analyzer = WealthDistributionAnalyzer()
        >>> gini = analyzer.calculate_gini(agents)
        >>> percentiles = analyzer.get_wealth_percentiles(agents)
    """

    def calculate_gini(self, wealth_values: List[float]) -> float:
        """
        Calculate Gini coefficient for wealth distribution.

        Gini = 0 means perfect equality
        Gini = 1 means maximum inequality

        Args:
            wealth_values: List of wealth values

        Returns:
            float: Gini coefficient (0-1)
        """
        if not wealth_values or len(wealth_values) == 0:
            return 0.0

        n = len(wealth_values)
        if n == 1:
            return 0.0

        sorted_wealth = sorted(wealth_values)
        total_wealth = sum(sorted_wealth)

        if total_wealth == 0:
            return 0.0

        # Calculate Gini using the formula
        cumulative = 0.0
        for i, wealth in enumerate(sorted_wealth):
            cumulative += (n - i) * wealth

        gini = (n + 1 - 2 * cumulative / total_wealth) / n
        return max(0.0, min(1.0, gini))

    def get_wealth_percentiles(
        self,
        wealth_values: List[float],
        percentiles: List[int] = None
    ) -> Dict[int, float]:
        """
        Calculate wealth at various percentiles.

        Args:
            wealth_values: List of wealth values
            percentiles: Percentiles to calculate (default: 10,25,50,75,90)

        Returns:
            Dict mapping percentile to wealth value
        """
        if percentiles is None:
            percentiles = [10, 25, 50, 75, 90]

        if not wealth_values:
            return {p: 0.0 for p in percentiles}

        sorted_wealth = sorted(wealth_values)
        n = len(sorted_wealth)

        result = {}
        for p in percentiles:
            idx = int((p / 100) * (n - 1))
            result[p] = sorted_wealth[idx]

        return result

    def get_distribution_summary(
        self,
        wealth_values: List[float]
    ) -> Dict[str, Any]:
        """
        Get comprehensive distribution summary.

        Args:
            wealth_values: List of wealth values

        Returns:
            Dict with distribution statistics
        """
        if not wealth_values:
            return {"error": "No data"}

        return {
            "count": len(wealth_values),
            "total": sum(wealth_values),
            "mean": statistics.mean(wealth_values),
            "median": statistics.median(wealth_values),
            "std_dev": statistics.stdev(wealth_values) if len(wealth_values) > 1 else 0,
            "min": min(wealth_values),
            "max": max(wealth_values),
            "gini": self.calculate_gini(wealth_values),
            "percentiles": self.get_wealth_percentiles(wealth_values),
        }


class FactionAnalyzer:
    """
    Analyzer for faction dynamics.

    Analyzes faction membership, growth, conflicts,
    and inter-faction relationships.

    Examples:
        >>> analyzer = FactionAnalyzer()
        >>> metrics = analyzer.analyze_faction(faction, agents)
    """

    def analyze_faction_health(
        self,
        faction_members: List[Agent]
    ) -> Dict[str, Any]:
        """
        Analyze health metrics of faction members.

        Args:
            faction_members: Agents in faction

        Returns:
            Dict with health metrics
        """
        if not faction_members:
            return {"error": "No members"}

        health_values = [a.health for a in faction_members]
        energy_values = [a.energy for a in faction_members]

        return {
            "member_count": len(faction_members),
            "total_health": sum(health_values),
            "average_health": statistics.mean(health_values),
            "min_health": min(health_values),
            "max_health": max(health_values),
            "total_energy": sum(energy_values),
            "average_energy": statistics.mean(energy_values),
            "critical_members": sum(1 for h in health_values if h < 20),
        }

    def calculate_faction_power(
        self,
        faction_members: List[Agent]
    ) -> float:
        """
        Calculate overall faction power.

        Power = sum of member combat potential.

        Args:
            faction_members: Agents in faction

        Returns:
            float: Total faction power
        """
        if not faction_members:
            return 0.0

        total_power = 0.0
        for agent in faction_members:
            strength = getattr(agent.traits, 'strength', 50)
            health_ratio = agent.health / agent.max_health if agent.max_health > 0 else 0
            total_power += strength * health_ratio

        return total_power


class SurvivalAnalyzer:
    """
    Analyzer for survival patterns.

    Tracks survival rates, lifespans, and causes
    of agent deaths.

    Examples:
        >>> analyzer = SurvivalAnalyzer()
        >>> rate = analyzer.get_survival_rate(agent_stats)
        >>> lifespans = analyzer.analyze_lifespans(agent_stats)
    """

    def get_survival_rate(
        self,
        agent_stats: Dict[str, AgentStatistics],
        at_step: Optional[int] = None
    ) -> float:
        """
        Calculate survival rate.

        Args:
            agent_stats: Agent statistics dict
            at_step: Calculate at specific step (None = current)

        Returns:
            float: Survival rate (0-1)
        """
        if not agent_stats:
            return 0.0

        alive = 0
        total = 0

        for stats in agent_stats.values():
            if at_step is None or stats.birth_step <= at_step:
                total += 1
                if stats.is_alive or (at_step is not None and
                    (stats.death_step is None or stats.death_step > at_step)):
                    alive += 1

        return alive / total if total > 0 else 0.0

    def analyze_lifespans(
        self,
        agent_stats: Dict[str, AgentStatistics]
    ) -> Dict[str, Any]:
        """
        Analyze agent lifespans.

        Args:
            agent_stats: Agent statistics dict

        Returns:
            Dict with lifespan analysis
        """
        lifespans = [
            stats.lifespan for stats in agent_stats.values()
            if stats.lifespan is not None
        ]

        if not lifespans:
            return {"error": "No completed lifespans"}

        return {
            "sample_size": len(lifespans),
            "mean_lifespan": statistics.mean(lifespans),
            "median_lifespan": statistics.median(lifespans),
            "min_lifespan": min(lifespans),
            "max_lifespan": max(lifespans),
            "std_dev": statistics.stdev(lifespans) if len(lifespans) > 1 else 0,
        }

    def get_mortality_by_step(
        self,
        agent_stats: Dict[str, AgentStatistics],
        step_range: Optional[tuple] = None
    ) -> Dict[int, int]:
        """
        Get death counts by step.

        Args:
            agent_stats: Agent statistics dict
            step_range: Optional (start, end) step range

        Returns:
            Dict mapping step number to death count
        """
        mortality: Dict[int, int] = defaultdict(int)

        for stats in agent_stats.values():
            if stats.death_step is not None:
                if step_range is None or (
                    step_range[0] <= stats.death_step <= step_range[1]
                ):
                    mortality[stats.death_step] += 1

        return dict(mortality)
