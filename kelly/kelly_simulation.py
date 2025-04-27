import numpy as np
import matplotlib.pyplot as plt
from kelly import kfsingle, kfidouble
import os


def analyze_bankroll_growth(
    fractions, final_bankrolls, kelly_fraction, initial_bankroll
):
    """Analyze the relationship between betting fractions and final bankrolls."""
    # Convert final_bankrolls to numpy array
    final_bankrolls = np.array(final_bankrolls)

    # Calculate growth rates
    growth_rates = np.log(final_bankrolls / initial_bankroll)

    # Find maximum growth rate and corresponding fraction
    max_growth_idx = np.argmax(growth_rates)
    max_growth_fraction = fractions[max_growth_idx]
    max_growth_rate = growth_rates[max_growth_idx]

    # Calculate statistics
    mean_growth = np.mean(growth_rates)
    std_growth = np.std(growth_rates)

    print("\nBankroll Growth Analysis:")
    print(
        f"Maximum growth rate: {max_growth_rate:.4f} at fraction {max_growth_fraction:.4f}"
    )
    print(f"Kelly fraction: {kelly_fraction:.4f}")
    print(f"Mean growth rate: {mean_growth:.4f}")
    print(f"Standard deviation of growth: {std_growth:.4f}")

    return growth_rates


def simulate_single_bet(probabilities, returns, num_trials=1000, initial_bankroll=1000, image_dir="images"):
    """
    Simulate a single bet scenario using the Kelly Criterion.
    """
    kelly_fraction = kfsingle(returns, probabilities)
    print("\nSingle Bet Simulation:")
    print(f"Optimal Kelly Fraction: {kelly_fraction:.4f}")

    fractions = np.linspace(0, 2 * kelly_fraction, 20)
    final_bankrolls = []

    for fraction in fractions:
        bankroll = initial_bankroll
        for _ in range(num_trials):
            outcome = np.random.choice(len(probabilities), p=probabilities)
            bankroll *= 1 + fraction * returns[outcome]
        final_bankrolls.append(bankroll)

    growth_rates = analyze_bankroll_growth(
        fractions, final_bankrolls, kelly_fraction, initial_bankroll
    )

    # Only plot growth rate vs betting fraction (Plot 2)
    plt.figure(figsize=(10, 6))
    plt.plot(fractions, growth_rates, "g-", label="Growth Rate")
    plt.axvline(x=kelly_fraction, color="r", linestyle="--", label="Kelly Fraction")
    plt.xlabel("Betting Fraction")
    plt.ylabel("Log Growth Rate")
    plt.title("Growth Rate vs Betting Fraction")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    os.makedirs(image_dir, exist_ok=True)
    plt.savefig(os.path.join(image_dir, "single_bet_growth_rate.png"))
    plt.close()


def simulate_double_bet(
    probabilities1,
    returns1,
    probabilities2,
    returns2,
    num_trials=1000,
    initial_bankroll=1000,
    image_dir="images"
):
    """
    Simulate two independent bets using the Kelly Criterion.
    """
    if initial_bankroll <= 0:
        raise ValueError("initial_bankroll must be positive and non-zero.")
    kelly_fractions = kfidouble(returns1, returns2, probabilities1, probabilities2)
    print("\nDouble Bet Simulation:")
    print(
        f"Optimal Kelly Fractions: {kelly_fractions[0]:.4f}, {kelly_fractions[1]:.4f}"
    )

    fractions1 = np.linspace(0, 2 * kelly_fractions[0], 10)
    fractions2 = np.linspace(0, 2 * kelly_fractions[1], 10)
    final_bankrolls = np.zeros((len(fractions1), len(fractions2)))
    growth_rates = np.zeros((len(fractions1), len(fractions2)))

    for i, f1 in enumerate(fractions1):
        for j, f2 in enumerate(fractions2):
            bankroll = initial_bankroll
            for _ in range(num_trials):
                outcome1 = np.random.choice(len(probabilities1), p=probabilities1)
                outcome2 = np.random.choice(len(probabilities2), p=probabilities2)
                bankroll *= 1 + f1 * returns1[outcome1] + f2 * returns2[outcome2]
            final_bankrolls[i, j] = bankroll
            # Avoid log of zero or negative values
            if bankroll > 0:
                growth_rates[i, j] = np.log(bankroll / initial_bankroll)
            else:
                growth_rates[i, j] = float('-inf')

    max_growth_idx = np.unravel_index(np.argmax(growth_rates), growth_rates.shape)
    max_growth_f1 = fractions1[max_growth_idx[0]]
    max_growth_f2 = fractions2[max_growth_idx[1]]
    max_growth_rate = growth_rates[max_growth_idx]

    print("\nBankroll Growth Analysis:")
    print(f"Maximum growth rate: {max_growth_rate:.4f}")
    print(f"At fractions: {max_growth_f1:.4f}, {max_growth_f2:.4f}")
    print(f"Kelly fractions: {kelly_fractions[0]:.4f}, {kelly_fractions[1]:.4f}")

    # Only plot growth rate contour (Plot 2)
    plt.figure(figsize=(10, 8))
    contour = plt.contourf(fractions1, fractions2, growth_rates, levels=20)
    plt.colorbar(contour, label="Log Growth Rate")
    plt.scatter(
        kelly_fractions[0], kelly_fractions[1], color="red", label="Kelly Fractions"
    )
    plt.xlabel("Bet 1 Fraction")
    plt.ylabel("Bet 2 Fraction")
    plt.title("Growth Rate Contour")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    os.makedirs(image_dir, exist_ok=True)
    plt.savefig(os.path.join(image_dir, "double_bet_growth_rate_contour.png"))
    plt.close()


def simulate_bankroll_trajectories(
    probabilities, returns, num_steps=50, num_trials=10000, initial_bankroll=1.0, image_dir="images"
):
    """
    Simulate multiple bankroll trajectories over time using the Kelly fraction.
    """
    kelly_fraction = kfsingle(returns, probabilities)
    print(
        f"\nSimulating {num_trials} paths for {num_steps} years at Kelly fraction {kelly_fraction:.4f}"
    )

    bankrolls = np.zeros((num_trials, num_steps + 1))
    bankrolls[:, 0] = initial_bankroll

    for trial in range(num_trials):
        bankroll = initial_bankroll
        for t in range(1, num_steps + 1):
            outcome = np.random.choice(len(probabilities), p=probabilities)
            bankroll *= 1 + kelly_fraction * returns[outcome]
            bankrolls[trial, t] = bankroll

    p5 = np.percentile(bankrolls, 5, axis=0)
    p95 = np.percentile(bankrolls, 95, axis=0)
    p50 = np.percentile(bankrolls, 50, axis=0)
    p10 = np.percentile(bankrolls, 10, axis=0)
    p90 = np.percentile(bankrolls, 90, axis=0)
    mean = np.mean(bankrolls, axis=0)

    years = np.arange(num_steps + 1)
    plt.figure(figsize=(12, 8))
    for i in range(min(100, num_trials)):
        plt.plot(years, bankrolls[i], color="gray", alpha=0.2, linewidth=0.7)
    plt.fill_between(
        years, p5, p95, color="gray", alpha=0.4, label="5th & 95th Percentile"
    )
    plt.fill_between(
        years, p10, p90, color="gray", alpha=0.2, label="10th & 90th Percentile"
    )
    plt.plot(years, p50, "k-", linewidth=2, label="Median")
    plt.plot(years, mean, "k--", linewidth=2, label="Mean")
    plt.yscale("log")
    plt.xlabel("Years")
    plt.ylabel("Ending Wealth")
    plt.title(
        f"{num_trials:,} Paths of {num_steps}-year Compounded Returns at Kelly Fraction"
    )
    plt.legend()
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.tight_layout()
    os.makedirs(image_dir, exist_ok=True)
    plt.savefig(os.path.join(image_dir, "single_bet_trajectories.png"))
    plt.close()


def simulate_double_bet_trajectories(
    probabilities1,
    returns1,
    probabilities2,
    returns2,
    num_steps=50,
    num_trials=10000,
    initial_bankroll=1.0,
    image_dir="images"
):
    """
    Simulate multiple bankroll trajectories over time for two independent bets using Kelly fractions.
    """
    kelly_fractions = kfidouble(returns1, returns2, probabilities1, probabilities2)
    f1, f2 = kelly_fractions
    print(
        f"\nSimulating {num_trials} paths for {num_steps} years at Kelly fractions {f1:.4f}, {f2:.4f}"
    )

    bankrolls = np.zeros((num_trials, num_steps + 1))
    bankrolls[:, 0] = initial_bankroll

    for trial in range(num_trials):
        bankroll = initial_bankroll
        for t in range(1, num_steps + 1):
            outcome1 = np.random.choice(len(probabilities1), p=probabilities1)
            outcome2 = np.random.choice(len(probabilities2), p=probabilities2)
            bankroll *= 1 + f1 * returns1[outcome1] + f2 * returns2[outcome2]
            bankrolls[trial, t] = bankroll

    p5 = np.percentile(bankrolls, 5, axis=0)
    p95 = np.percentile(bankrolls, 95, axis=0)
    p50 = np.percentile(bankrolls, 50, axis=0)
    p10 = np.percentile(bankrolls, 10, axis=0)
    p90 = np.percentile(bankrolls, 90, axis=0)
    mean = np.mean(bankrolls, axis=0)

    years = np.arange(num_steps + 1)
    plt.figure(figsize=(12, 8))
    for i in range(min(100, num_trials)):
        plt.plot(years, bankrolls[i], color="gray", alpha=0.2, linewidth=0.7)
    plt.fill_between(
        years, p5, p95, color="gray", alpha=0.4, label="5th & 95th Percentile"
    )
    plt.fill_between(
        years, p10, p90, color="gray", alpha=0.2, label="10th & 90th Percentile"
    )
    plt.plot(years, p50, "k-", linewidth=2, label="Median")
    plt.plot(years, mean, "k--", linewidth=2, label="Mean")
    plt.yscale("log")
    plt.xlabel("Years")
    plt.ylabel("Ending Wealth")
    plt.title(
        f"{num_trials:,} Paths of {num_steps}-year Compounded Returns at Double Kelly Fractions"
    )
    plt.legend()
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.tight_layout()
    os.makedirs(image_dir, exist_ok=True)
    plt.savefig(os.path.join(image_dir, "double_bet_trajectories.png"))
    plt.close()


if __name__ == "__main__":

    # Set random seed for reproducibility
    np.random.seed(42)

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

    # Replace one of the main examples with the new function
    print(
        "Example: Kelly Fraction Trajectories for Biased Coin Flip (60% win, 1:1 payout)"
    )
    probabilities = [0.6, 0.4]
    returns = [1.0, -1.0]
    simulate_bankroll_trajectories(
        probabilities, returns, num_steps=50, num_trials=10000, initial_bankroll=1.0
    )

    # Example usage in main
    print("Example: Double Kelly Fraction Trajectories for Two Independent Bets")
    probabilities1 = [0.6, 0.4]  # First bet: 60% chance of winning
    returns1 = [1.0, -1.0]  # Win 100% or lose 100%
    probabilities2 = [0.7, 0.3]  # Second bet: 70% chance of winning
    returns2 = [0.5, -0.5]  # Win 50% or lose 50%
    simulate_double_bet_trajectories(
        probabilities1,
        returns1,
        probabilities2,
        returns2,
        num_steps=50,
        num_trials=10000,
        initial_bankroll=1.0,
    )
