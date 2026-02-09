"""Tests for Timeline."""

from __future__ import annotations

import pytest

from monteplan.core.timeline import Timeline


class TestTimeline:
    def test_step_counts(self) -> None:
        tl = Timeline.from_ages(30, 65, 95)
        assert tl.n_steps == 780  # 65 years * 12
        assert tl.retirement_step == 420  # 35 years * 12

    def test_retirement_check(self) -> None:
        tl = Timeline.from_ages(30, 65, 95)
        assert not tl.is_retired(0)
        assert not tl.is_retired(419)
        assert tl.is_retired(420)
        assert tl.is_retired(780)

    def test_income_check(self) -> None:
        tl = Timeline.from_ages(30, 65, 95, income_end_age=60)
        assert tl.has_income(0)
        assert tl.has_income(359)  # last month before 60
        assert not tl.has_income(360)  # age 60

    def test_income_defaults_to_retirement(self) -> None:
        tl = Timeline.from_ages(30, 65, 95)
        assert tl.income_end_step == tl.retirement_step

    def test_age_at(self) -> None:
        tl = Timeline.from_ages(30, 65, 95)
        assert tl.age_at(0) == 30.0
        assert tl.age_at(12) == 31.0
        assert tl.age_at(6) == pytest.approx(30.5)

    def test_month_of_year(self) -> None:
        tl = Timeline.from_ages(30, 65, 95)
        assert tl.month_of_year(0) == 1  # January
        assert tl.month_of_year(1) == 2
        assert tl.month_of_year(11) == 12
        assert tl.month_of_year(12) == 1  # wraps

    def test_short_horizon(self) -> None:
        tl = Timeline.from_ages(60, 65, 70)
        assert tl.n_steps == 120
        assert tl.retirement_step == 60
