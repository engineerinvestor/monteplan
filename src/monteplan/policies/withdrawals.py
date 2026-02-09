"""Withdrawal ordering policy: taxable -> traditional -> roth."""

from __future__ import annotations

import numpy as np

from monteplan.core.state import SimulationState


def withdraw(
    state: SimulationState,
    amount_needed: np.ndarray,
    withdrawal_order: list[str],
    tax_rate: float,
) -> np.ndarray:
    """Withdraw from accounts in priority order.

    For traditional accounts, gross up the withdrawal to cover taxes:
    to get $X after tax, withdraw $X / (1 - tax_rate).

    Args:
        state: Current simulation state (balances will be mutated).
        amount_needed: (n_paths,) after-tax spending needed.
        withdrawal_order: Priority list of account types.
        tax_rate: Flat effective tax rate on traditional withdrawals.

    Returns:
        (n_paths,) actual after-tax amount withdrawn (may be less than needed
        if accounts are depleted).
    """
    remaining = amount_needed.copy()
    total_withdrawn_after_tax = np.zeros(state.n_paths)

    for acct_type in withdrawal_order:
        # Find accounts of this type
        indices = [i for i, t in enumerate(state.account_types) if t == acct_type]
        if not indices:
            continue

        for idx in indices:
            available = state.balances[:, idx]
            done = remaining <= 0

            if acct_type == "traditional":
                # Need to withdraw more to cover taxes
                gross_factor = 1.0 / (1.0 - tax_rate)
                gross_needed = remaining * gross_factor
                gross_withdraw = np.minimum(gross_needed, available)
                after_tax = gross_withdraw * (1.0 - tax_rate)
            else:
                # Taxable and Roth: no additional tax on withdrawal
                # (simplified: ignoring capital gains on taxable)
                gross_withdraw = np.minimum(remaining, available)
                after_tax = gross_withdraw

            # Don't withdraw from paths that are done
            gross_withdraw = np.where(done, 0.0, gross_withdraw)
            after_tax = np.where(done, 0.0, after_tax)

            state.balances[:, idx] -= gross_withdraw
            remaining -= after_tax
            total_withdrawn_after_tax += after_tax

    return total_withdrawn_after_tax
