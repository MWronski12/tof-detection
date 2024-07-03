import pytest

from utils import split_to_non_zero_sequences, split_to_monotonic_sequences, split_to_non_zero_monotonic_series


class TestSplitToNonZeroSequences:

    def test_corner(self):
        samples = []
        assert len(split_to_non_zero_sequences(samples)) == 0

        samples = [(0, -1)]
        assert len(split_to_non_zero_sequences(samples)) == 0

        samples = [(0, 1)]
        assert len(split_to_non_zero_sequences(samples)) == 1

    def test_basic(self):
        samples = [(0, -1), (0, -1), (0, 4), (0, 5), (0, 6), (0, -1), (0, -1), (0, -1), (0, 2), (0, 3), (0, -1)]
        splitted = split_to_non_zero_sequences(samples)

        assert len(splitted) == 2
        assert splitted[0] == [(0, 4), (0, 5), (0, 6)]
        assert splitted[1] == [(0, 2), (0, 3)]


class TestSplitToMonotonicSequences:

    def test_corner(self):
        samples = []
        assert len(split_to_monotonic_sequences(samples)) == 0

        samples = [(0, 1)]
        splitted = split_to_monotonic_sequences(samples)
        assert len(splitted) == 1
        assert splitted[0] == [(0, 1)]

        samples = [(0, 1), (0, 1)]
        splitted = split_to_monotonic_sequences(samples)
        assert len(splitted) == 1
        assert splitted[0] == [(0, 1), (0, 1)]

    def test_basic(self):
        samples = [(0, 4), (0, 5), (0, 6), (0, 2), (0, 3), (0, 1), (0, 2)]
        splitted = split_to_monotonic_sequences(samples)

        assert len(splitted) == 3
        assert splitted[0] == [(0, 4), (0, 5), (0, 6)]
        assert splitted[1] == [(0, 2), (0, 3)]
        assert splitted[2] == [(0, 1), (0, 2)]


class TestSplitToNonZeroMonotonicSequences:

    def test_corner(self):
        samples = []
        assert len(split_to_non_zero_monotonic_series(samples)) == 0

        samples = [(0, -1)]
        splitted = split_to_non_zero_monotonic_series(samples)
        assert len(splitted) == 0

        samples = [(0, 1)]
        splitted = split_to_non_zero_monotonic_series(samples)
        assert len(splitted) == 1
        assert splitted[0] == [(0, 1)]

    def test_basic(self):
        samples = [
            (0, -1),
            (0, 5),
            (0, 4),
            (0, 3),
            (0, 5),
            (0, 6),
            (0, 7),
            (0, -1),
            (0, -1),
            (0, 8),
            (0, 6),
            (0, 7),
            (0, 6),
            (0, 7),
            (0, 8),
            (0, 9),
            (0, -1),
            (0, -1),
            (0, 3),
            (0, -1),
        ]
        splitted = split_to_non_zero_monotonic_series(samples)

        assert len(splitted) == 6
        assert splitted[0] == [(0, 5), (0, 4), (0, 3)]
        assert splitted[1] == [(0, 5), (0, 6), (0, 7)]
        assert splitted[2] == [(0, 8), (0, 6)]
        assert splitted[3] == [(0, 7), (0, 6)]
        assert splitted[4] == [(0, 7), (0, 8), (0, 9)]
        assert splitted[5] == [(0, 3)]
