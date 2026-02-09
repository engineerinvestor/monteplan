"""Monthly timeline for simulation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Timeline:
    """Monthly time grid derived from plan ages.

    Attributes:
        current_age: Starting age in years.
        retirement_age: Retirement age in years.
        end_age: End of simulation age in years.
        income_end_age: Age when earned income stops.
        n_steps: Total number of monthly steps.
        retirement_step: Step index when retirement begins.
        income_end_step: Step index when income stops.
    """

    current_age: int
    retirement_age: int
    end_age: int
    income_end_age: int
    n_steps: int
    retirement_step: int
    income_end_step: int

    @classmethod
    def from_ages(
        cls,
        current_age: int,
        retirement_age: int,
        end_age: int,
        income_end_age: int | None = None,
    ) -> Timeline:
        """Create a Timeline from age parameters."""
        if income_end_age is None:
            income_end_age = retirement_age
        n_steps = (end_age - current_age) * 12
        retirement_step = (retirement_age - current_age) * 12
        income_end_step = (income_end_age - current_age) * 12
        return cls(
            current_age=current_age,
            retirement_age=retirement_age,
            end_age=end_age,
            income_end_age=income_end_age,
            n_steps=n_steps,
            retirement_step=retirement_step,
            income_end_step=income_end_step,
        )

    def is_retired(self, step: int) -> bool:
        """Check if the simulation is in the retirement phase at a given step."""
        return step >= self.retirement_step

    def has_income(self, step: int) -> bool:
        """Check if earned income is active at a given step."""
        return step < self.income_end_step

    def age_at(self, step: int) -> float:
        """Return the age (as a float) at a given step."""
        return self.current_age + step / 12.0

    def month_of_year(self, step: int) -> int:
        """Return the calendar month (1-12) at a given step.

        Assumes the simulation starts in January.
        """
        return (step % 12) + 1
