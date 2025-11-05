#!/usr/bin/env python3
"""
Example script demonstrating how to interact with the WebShop environment using RAGEN.

This script shows:
1. How to create a WebShop environment
2. How to perform a simple interaction loop
3. How to parse observations and take actions
4. Basic agent logic for shopping
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ragen.env.webshop.env import WebShopEnv
from ragen.env.webshop.config import WebShopEnvConfig


def simple_agent_policy(observation: str, action_count: int) -> str:
    """
    A simple rule-based policy for demonstration purposes.
    In real RAGEN training, this is replaced by LLM generation.

    Args:
        observation: Current observation from the environment
        action_count: Number of actions taken so far

    Returns:
        Action string to take
    """
    obs_lower = observation.lower()

    # If we're at the initial search page
    if "webshop [sep] instruction:" in obs_lower and "search" in obs_lower:
        # Extract instruction
        if "instruction:" in obs_lower:
            instruction_part = observation.split("[SEP]")[1] if "[SEP]" in observation else ""
            # Simple search based on instruction
            print(f"\n[AGENT] First action: searching based on instruction")
            return "search[laptop computer]"

    # If we're on a search results page
    elif "back to search" in obs_lower and ("next >" in obs_lower or "[sep] b0" in obs_lower):
        # Look for product IDs (usually start with B0)
        if "b09" in obs_lower or "b07" in obs_lower or "b08" in obs_lower:
            # Extract first product ID
            import re
            product_ids = re.findall(r'b[0-9][0-9a-z]+', obs_lower)
            if product_ids and action_count < 3:
                print(f"\n[AGENT] Found products, clicking on: {product_ids[0]}")
                return f"click[{product_ids[0]}]"

        # If no products or already viewed some, maybe go to next page
        if "next >" in obs_lower and action_count < 2:
            print(f"\n[AGENT] Going to next page")
            return "click[next >]"

    # If we're on a product page
    elif "buy now" in obs_lower:
        # Check if we need to select attributes
        if "size [sep]" in obs_lower and action_count < 7:
            # Try to select a size
            sizes = ["large", "medium", "small"]
            for size in sizes:
                if size in obs_lower:
                    print(f"\n[AGENT] Selecting size: {size}")
                    return f"click[{size}]"

        if "color [sep]" in obs_lower and action_count < 8:
            # Try to select a color
            colors = ["black", "blue", "red", "white", "gray"]
            for color in colors:
                if color in obs_lower:
                    print(f"\n[AGENT] Selecting color: {color}")
                    return f"click[{color}]"

        # If attributes are selected or running out of actions, buy
        print(f"\n[AGENT] Ready to purchase")
        return "click[buy now]"

    # Default: if nothing else matches and we have a product page, try to buy
    if "buy now" in obs_lower:
        print(f"\n[AGENT] Default action: buy now")
        return "click[buy now]"

    # Fallback: search for something generic
    print(f"\n[AGENT] Fallback: new search")
    return "search[product]"


def run_episode(env: WebShopEnv, session_id: int = 0, max_actions: int = 10, verbose: bool = True):
    """
    Run a single episode in the WebShop environment.

    Args:
        env: WebShop environment instance
        session_id: Session ID to use for this episode
        max_actions: Maximum number of actions to take
        verbose: Whether to print detailed information

    Returns:
        Tuple of (total_reward, done, action_count)
    """
    print(f"\n{'=' * 70}")
    print(f"Starting Episode with Session ID: {session_id}")
    print(f"{'=' * 70}")

    # Reset environment
    obs = env.reset(seed=session_id, mode="train")

    if verbose:
        print(f"\n[Initial Observation]")
        print("-" * 70)
        print(obs[:800])  # Print first 800 characters
        if len(obs) > 800:
            print(f"... ({len(obs) - 800} more characters)")
        print("-" * 70)

    total_reward = 0
    done = False
    action_count = 0

    # Interaction loop
    for step in range(max_actions):
        # Get action from policy
        action = simple_agent_policy(obs, action_count)

        print(f"\n[Step {step + 1}] Action: {action}")

        # Take step in environment
        try:
            obs, reward, done, info = env.step(action)
            total_reward += reward
            action_count += 1

            if verbose:
                print(f"[Step {step + 1}] Reward: {reward:.4f}, Total: {total_reward:.4f}, Done: {done}")
                print(f"\n[Observation after action]")
                print("-" * 70)
                print(obs[:600])  # Print first 600 characters
                if len(obs) > 600:
                    print(f"... ({len(obs) - 600} more characters)")
                print("-" * 70)

            if done:
                print(f"\n✓ Episode completed!")
                break

        except Exception as e:
            print(f"\n✗ Error taking step: {e}")
            import traceback
            traceback.print_exc()
            break

    print(f"\n{'=' * 70}")
    print(f"Episode Summary")
    print(f"{'=' * 70}")
    print(f"Total Actions: {action_count}")
    print(f"Total Reward: {total_reward:.4f}")
    print(f"Episode Completed: {done}")
    print(f"{'=' * 70}\n")

    return total_reward, done, action_count


def main():
    """Main function to run the example"""
    print("\n" + "=" * 70)
    print("RAGEN WebShop Environment Example")
    print("=" * 70)
    print("\nThis example demonstrates basic interaction with the WebShop environment.")
    print("Note: This uses a simple rule-based agent, not the trained LLM agent.\n")

    # Create environment
    print("[1] Creating WebShop environment...")
    config = WebShopEnvConfig(
        dataset="small",  # Use small dataset for faster loading
        observation_mode="text"
    )

    try:
        env = WebShopEnv(config=config)
        print("✓ Environment created successfully\n")
    except Exception as e:
        print(f"✗ Failed to create environment: {e}")
        print("\nPlease ensure you have run:")
        print("  bash scripts/setup_webshop.sh")
        return

    # Run a few episodes
    print("[2] Running example episodes...")
    num_episodes = 2

    episode_results = []
    for episode_id in range(num_episodes):
        reward, done, actions = run_episode(
            env,
            session_id=episode_id,
            max_actions=9,
            verbose=True
        )
        episode_results.append((reward, done, actions))

    # Print overall summary
    print("\n" + "=" * 70)
    print("Overall Summary")
    print("=" * 70)
    for i, (reward, done, actions) in enumerate(episode_results):
        print(f"Episode {i + 1}: Reward={reward:.4f}, Done={done}, Actions={actions}")

    avg_reward = sum(r for r, _, _ in episode_results) / len(episode_results)
    print(f"\nAverage Reward: {avg_reward:.4f}")
    print("=" * 70)

    print("\n[Next Steps]")
    print("-" * 70)
    print("To train an LLM agent with RAGEN:")
    print("  python train.py --config-name _6_webshop")
    print("\nOr use the quick start script:")
    print("  bash scripts/quick_start_webshop.sh")
    print("\nFor more information, see:")
    print("  WEBSHOP_REPRODUCTION_GUIDE.md")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
