"""Tests for Position class - Immutable Pattern Validation.

This module tests the Position value object, with focus on validating
the Immutable pattern implementation using frozen dataclass.
"""
import pytest
import math
from dataclasses import FrozenInstanceError

import sys
import os
src_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src')
sys.path.insert(0, src_path)
sys.path.insert(0, os.path.join(src_path, 'world'))

from position import Position


# ============================================================================
# BASIC CREATION AND PROPERTIES
# ============================================================================

class TestPositionCreation:
    """Test basic position creation and properties."""

    def test_position_creation(self):
        """Test creating a position with valid coordinates."""
        pos = Position(5, 10)
        assert pos.x == 5
        assert pos.y == 10

    def test_position_creation_negative_coordinates(self):
        """Test that positions can have negative coordinates."""
        pos = Position(-3, -7)
        assert pos.x == -3
        assert pos.y == -7

    def test_position_creation_zero(self):
        """Test creating position at origin."""
        pos = Position(0, 0)
        assert pos.x == 0
        assert pos.y == 0

    def test_position_equality(self):
        """Test that positions with same coordinates are equal."""
        pos1 = Position(5, 10)
        pos2 = Position(5, 10)
        assert pos1 == pos2

    def test_position_inequality(self):
        """Test that positions with different coordinates are not equal."""
        pos1 = Position(5, 10)
        pos2 = Position(10, 5)
        assert pos1 != pos2


# ============================================================================
# IMMUTABILITY TESTS (CRITICAL FOR PATTERN VALIDATION)
# ============================================================================

@pytest.mark.pattern
class TestPositionImmutability:
    """Test immutable pattern implementation - CRITICAL."""

    def test_position_immutability_x(self):
        """Validate Immutable pattern - cannot modify x after creation."""
        pos = Position(5, 10)
        with pytest.raises(FrozenInstanceError):
            pos.x = 10

    def test_position_immutability_y(self):
        """Validate Immutable pattern - cannot modify y after creation."""
        pos = Position(5, 10)
        with pytest.raises(FrozenInstanceError):
            pos.y = 20

    def test_position_hashable(self):
        """Test that immutable positions can be used as dict keys."""
        pos1 = Position(5, 10)
        pos2 = Position(5, 10)
        pos3 = Position(8, 15)

        # Should be able to use as dict keys
        position_dict = {pos1: "location1", pos3: "location2"}
        assert position_dict[pos2] == "location1"  # Same value, same key
        assert len(position_dict) == 2

    def test_position_in_set(self):
        """Test that positions can be added to sets (requires immutability)."""
        positions = {Position(1, 1), Position(2, 2), Position(1, 1)}
        # Duplicate should be removed
        assert len(positions) == 2


# ============================================================================
# DISTANCE CALCULATIONS
# ============================================================================

class TestPositionDistances:
    """Test distance calculation methods."""

    def test_distance_to_self_is_zero(self):
        """Test that distance from position to itself is zero."""
        pos = Position(5, 10)
        assert pos.distance_to(pos) == 0.0

    def test_euclidean_distance_horizontal(self):
        """Test Euclidean distance along horizontal line."""
        pos1 = Position(0, 0)
        pos2 = Position(3, 0)
        expected = 3.0
        assert pos1.distance_to(pos2) == pytest.approx(expected)

    def test_euclidean_distance_vertical(self):
        """Test Euclidean distance along vertical line."""
        pos1 = Position(0, 0)
        pos2 = Position(0, 4)
        expected = 4.0
        assert pos1.distance_to(pos2) == pytest.approx(expected)

    def test_euclidean_distance_diagonal(self):
        """Test Euclidean distance along diagonal."""
        pos1 = Position(0, 0)
        pos2 = Position(3, 4)
        expected = 5.0  # 3-4-5 triangle
        assert pos1.distance_to(pos2) == pytest.approx(expected)

    def test_manhattan_distance(self):
        """Test Manhattan (taxicab) distance calculation."""
        pos1 = Position(1, 2)
        pos2 = Position(4, 6)
        # |4-1| + |6-2| = 3 + 4 = 7
        expected = 7
        assert pos1.manhattan_distance_to(pos2) == expected

    def test_manhattan_distance_same_position(self):
        """Test Manhattan distance to self is zero."""
        pos = Position(5, 5)
        assert pos.manhattan_distance_to(pos) == 0

    def test_manhattan_distance_negative_coords(self):
        """Test Manhattan distance with negative coordinates."""
        pos1 = Position(-2, -3)
        pos2 = Position(1, 2)
        # |1-(-2)| + |2-(-3)| = 3 + 5 = 8
        expected = 8
        assert pos1.manhattan_distance_to(pos2) == expected


# ============================================================================
# NEIGHBOR DETECTION
# ============================================================================

class TestPositionNeighbors:
    """Test neighbor detection and adjacency methods."""

    def test_get_neighbors_cardinal_only(self):
        """Test getting only cardinal (N, S, E, W) neighbors."""
        pos = Position(5, 5)
        neighbors = pos.get_neighbors(include_diagonals=False)

        expected = {
            Position(5, 4),  # North
            Position(5, 6),  # South
            Position(6, 5),  # East
            Position(4, 5),  # West
        }

        assert len(neighbors) == 4
        assert set(neighbors) == expected

    def test_get_neighbors_with_diagonals(self):
        """Test getting all 8 neighbors including diagonals."""
        pos = Position(5, 5)
        neighbors = pos.get_neighbors(include_diagonals=True)

        expected = {
            Position(5, 4),  # N
            Position(5, 6),  # S
            Position(6, 5),  # E
            Position(4, 5),  # W
            Position(4, 4),  # NW
            Position(6, 4),  # NE
            Position(4, 6),  # SW
            Position(6, 6),  # SE
        }

        assert len(neighbors) == 8
        assert set(neighbors) == expected

    def test_get_neighbors_at_origin(self):
        """Test neighbors at origin include negative coordinates."""
        pos = Position(0, 0)
        neighbors = pos.get_neighbors(include_diagonals=False)

        expected = {
            Position(0, -1),  # North
            Position(0, 1),   # South
            Position(1, 0),   # East
            Position(-1, 0),  # West
        }

        assert set(neighbors) == expected

    def test_is_adjacent_cardinal(self):
        """Test adjacency detection for cardinal neighbors."""
        center = Position(5, 5)

        # Cardinal neighbors
        assert center.is_adjacent_to(Position(5, 4), include_diagonals=False)  # N
        assert center.is_adjacent_to(Position(5, 6), include_diagonals=False)  # S
        assert center.is_adjacent_to(Position(6, 5), include_diagonals=False)  # E
        assert center.is_adjacent_to(Position(4, 5), include_diagonals=False)  # W

    def test_is_adjacent_diagonal(self):
        """Test adjacency detection for diagonal neighbors."""
        center = Position(5, 5)

        # Diagonal neighbors should not be adjacent with include_diagonals=False
        assert not center.is_adjacent_to(Position(4, 4), include_diagonals=False)
        assert not center.is_adjacent_to(Position(6, 6), include_diagonals=False)

        # But should be adjacent with include_diagonals=True
        assert center.is_adjacent_to(Position(4, 4), include_diagonals=True)
        assert center.is_adjacent_to(Position(6, 6), include_diagonals=True)

    def test_is_adjacent_not_neighbors(self):
        """Test that non-adjacent positions are correctly identified."""
        center = Position(5, 5)
        assert not center.is_adjacent_to(Position(7, 7), include_diagonals=True)
        assert not center.is_adjacent_to(Position(5, 10), include_diagonals=True)
        assert not center.is_adjacent_to(Position(0, 0), include_diagonals=False)

    def test_is_adjacent_to_self(self):
        """Test that a position is not adjacent to itself."""
        pos = Position(5, 5)
        assert not pos.is_adjacent_to(pos, include_diagonals=True)
        assert not pos.is_adjacent_to(pos, include_diagonals=False)


# ============================================================================
# BOUNDS CHECKING
# ============================================================================

class TestPositionBounds:
    """Test bounds checking functionality."""

    def test_is_within_bounds_valid(self):
        """Test position within valid bounds."""
        pos = Position(5, 5)
        assert pos.is_within_bounds(10, 10)

    def test_is_within_bounds_at_origin(self):
        """Test origin is within bounds."""
        pos = Position(0, 0)
        assert pos.is_within_bounds(10, 10)

    def test_is_within_bounds_at_max(self):
        """Test position at maximum valid coordinates."""
        pos = Position(9, 9)
        assert pos.is_within_bounds(10, 10)

    def test_is_within_bounds_x_negative(self):
        """Test negative x coordinate is out of bounds."""
        pos = Position(-1, 5)
        assert not pos.is_within_bounds(10, 10)

    def test_is_within_bounds_y_negative(self):
        """Test negative y coordinate is out of bounds."""
        pos = Position(5, -1)
        assert not pos.is_within_bounds(10, 10)

    def test_is_within_bounds_x_too_large(self):
        """Test x coordinate >= width is out of bounds."""
        pos = Position(10, 5)
        assert not pos.is_within_bounds(10, 10)

    def test_is_within_bounds_y_too_large(self):
        """Test y coordinate >= height is out of bounds."""
        pos = Position(5, 10)
        assert not pos.is_within_bounds(10, 10)

    def test_is_within_bounds_both_out(self):
        """Test both coordinates out of bounds."""
        pos = Position(15, 20)
        assert not pos.is_within_bounds(10, 10)


# ============================================================================
# CONVERSION METHODS
# ============================================================================

class TestPositionConversions:
    """Test conversion and string representation methods."""

    def test_to_tuple(self):
        """Test conversion to tuple."""
        pos = Position(5, 10)
        assert pos.to_tuple() == (5, 10)

    def test_to_tuple_negative(self):
        """Test tuple conversion with negative coordinates."""
        pos = Position(-3, -7)
        assert pos.to_tuple() == (-3, -7)

    def test_str_representation(self):
        """Test string representation."""
        pos = Position(5, 10)
        result = str(pos)
        assert "5" in result
        assert "10" in result

    def test_repr_representation(self):
        """Test repr representation."""
        pos = Position(5, 10)
        result = repr(pos)
        assert "5" in result
        assert "10" in result
        assert "Position" in result


# ============================================================================
# EDGE CASES AND SPECIAL SCENARIOS
# ============================================================================

class TestPositionEdgeCases:
    """Test edge cases and special scenarios."""

    def test_large_coordinates(self):
        """Test positions with very large coordinates."""
        pos = Position(10000, 10000)
        assert pos.x == 10000
        assert pos.y == 10000

    def test_distance_symmetry(self):
        """Test that distance(A, B) == distance(B, A)."""
        pos1 = Position(2, 3)
        pos2 = Position(7, 9)
        assert pos1.distance_to(pos2) == pos2.distance_to(pos1)

    def test_manhattan_distance_symmetry(self):
        """Test Manhattan distance is symmetric."""
        pos1 = Position(2, 3)
        pos2 = Position(7, 9)
        assert pos1.manhattan_distance_to(pos2) == pos2.manhattan_distance_to(pos1)

    def test_position_equality_with_tuple_unpack(self):
        """Test position equality after unpacking."""
        x, y = 5, 10
        pos1 = Position(x, y)
        pos2 = Position(5, 10)
        assert pos1 == pos2

    def test_neighbors_count_cardinal(self):
        """Test that cardinal neighbors always returns 4 positions."""
        positions = [Position(0, 0), Position(5, 5), Position(100, 100)]
        for pos in positions:
            neighbors = pos.get_neighbors(include_diagonals=False)
            assert len(neighbors) == 4

    def test_neighbors_count_with_diagonals(self):
        """Test that all neighbors returns 8 positions."""
        positions = [Position(0, 0), Position(5, 5), Position(100, 100)]
        for pos in positions:
            neighbors = pos.get_neighbors(include_diagonals=True)
            assert len(neighbors) == 8
