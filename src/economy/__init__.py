"""
Economy System Package

This package provides economic simulation components including
pricing strategies, marketplaces, and trade tracking.

Modules:
    - pricing: Price calculation strategies (Strategy Pattern)
    - marketplace: Central market for trades (Mediator + Observer)

Design Patterns:
    - Strategy Pattern: Interchangeable pricing algorithms
    - Mediator Pattern: Marketplace coordinates trades
    - Observer Pattern: Market observers for events

SOLID Principles:
    - Single Responsibility: Each module has one purpose
    - Open/Closed: Extensible pricing strategies
    - Dependency Inversion: Depends on abstractions

Integration:
    - Uses inventory/resource_type.py for ResourceType
    - Uses inventory/transfer.py for transfers
    - Uses social/relationships.py for trade modifiers
"""

from economy.pricing import (
    PricingStrategy,
    FixedPricing,
    SupplyDemandPricing,
    RelationshipPricing,
    PriceTracker,
)
from economy.marketplace import (
    TradeOffer,
    TradeRecord,
    MarketplaceObserver,
    Marketplace,
    MarketplaceConfig,
)

__all__ = [
    # Pricing
    "PricingStrategy",
    "FixedPricing",
    "SupplyDemandPricing",
    "RelationshipPricing",
    "PriceTracker",
    # Marketplace
    "TradeOffer",
    "TradeRecord",
    "MarketplaceObserver",
    "Marketplace",
    "MarketplaceConfig",
]
