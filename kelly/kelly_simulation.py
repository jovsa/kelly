import numpy as np
import matplotlib.pyplot as plt
from kelly import kfsingle, kfidouble


def simulate_single_bet(probabilities, returns, num_trials=1000, initial_bankroll=1000):
    """
    Simulate a single bet scenario using the Kelly Criterion.

    Args:
        probabilities: List of probabilities for each outcome
        returns: List of returns for each outcome
        num_trials: Number of simulation trials
        initial_bankroll: Starting bankroll amount
    """
    # Calculate optimal Kelly fraction
    kelly_fraction = kfsingle(returns, probabilities)
    print("\nSingle Bet Simulation:")
    print(f"Optimal Kelly Fraction: {kelly_fraction:.4f}")

    # Simulate different betting fractions (from 0 to 2x Kelly)
    fractions = np.linspace(0, 2 * kelly_fraction, 20)
    final_bankrolls = []

    for fraction in fractions:
        bankroll = initial_bankroll
        for _ in range(num_trials):
            # Choose outcome based on probabilities
            outcome = np.random.choice(len(probabilities), p=probabilities)
            # Update bankroll
            bankroll *= 1 + fraction * returns[outcome]
        final_bankrolls.append(bankroll)

    # Plot results
    plt.figure(figsize=(10, 6))
    plt.plot(fractions, final_bankrolls, "b-", label="Final Bankroll")
    plt.axvline(x=kelly_fraction, color="r", linestyle="--", label="Kelly Fraction")
    plt.xlabel("Betting Fraction")
    plt.ylabel("Final Bankroll")
    plt.title("Single Bet Simulation Results")
    plt.legend()
    plt.grid(True)
    plt.show()


def simulate_double_bet(
    probabilities1,
    returns1,
    probabilities2,
    returns2,
    num_trials=1000,
    initial_bankroll=1000,
):
    """
    Simulate two independent bets using the Kelly Criterion.

    Args:
        probabilities1: List of probabilities for first bet
        returns1: List of returns for first bet
        probabilities2: List of probabilities for second bet
        returns2: List of returns for second bet
        num_trials: Number of simulation trials
        initial_bankroll: Starting bankroll amount
    """
    # Calculate optimal Kelly fractions
    kelly_fractions = kfidouble(returns1, returns2, probabilities1, probabilities2)
    print("\nDouble Bet Simulation:")
    print(
        f"Optimal Kelly Fractions: {kelly_fractions[0]:.4f}, {kelly_fractions[1]:.4f}"
    )

    # Simulate different betting fractions
    fractions1 = np.linspace(0, 2 * kelly_fractions[0], 10)
    fractions2 = np.linspace(0, 2 * kelly_fractions[1], 10)
    final_bankrolls = np.zeros((len(fractions1), len(fractions2)))

    for i, f1 in enumerate(fractions1):
        for j, f2 in enumerate(fractions2):
            bankroll = initial_bankroll
            for _ in range(num_trials):
                # Choose outcomes for both bets
                outcome1 = np.random.choice(len(probabilities1), p=probabilities1)
                outcome2 = np.random.choice(len(probabilities2), p=probabilities2)
                # Update bankroll
                bankroll *= 1 + f1 * returns1[outcome1] + f2 * returns2[outcome2]
            final_bankrolls[i, j] = bankroll

    # Plot results
    plt.figure(figsize=(10, 6))
    plt.contourf(fractions1, fractions2, final_bankrolls, levels=20)
    plt.colorbar(label="Final Bankroll")
    plt.scatter(
        kelly_fractions[0], kelly_fractions[1], color="red", label="Kelly Fractions"
    )
    plt.xlabel("Bet 1 Fraction")
    plt.ylabel("Bet 2 Fraction")
    plt.title("Double Bet Simulation Results")
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    # Example 1: Simple coin flip with 2:1 payout
    print("Example 1: Fair coin flip with 2:1 payout")
    probabilities = [0.5, 0.5]  # 50% chance of each outcome
    returns = [1.0, -0.5]  # Win 100% or lose 50%
    simulate_single_bet(probabilities, returns)

    # Example 2: Biased coin flip
    print("\nExample 2: Biased coin flip (60% chance of winning)")
    probabilities = [0.6, 0.4]
    returns = [1.0, -1.0]  # Win 100% or lose 100%
    simulate_single_bet(probabilities, returns)

    # Example 3: Two independent bets
    print("\nExample 3: Two independent bets")
    probabilities1 = [0.6, 0.4]  # First bet: 60% chance of winning
    returns1 = [1.0, -1.0]  # Win 100% or lose 100%
    probabilities2 = [0.7, 0.3]  # Second bet: 70% chance of winning
    returns2 = [0.5, -0.5]  # Win 50% or lose 50%
    simulate_double_bet(probabilities1, returns1, probabilities2, returns2)
