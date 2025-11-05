#!/usr/bin/env python3
"""
Test script to verify WebShop environment setup and basic functionality.
This script performs a simple interaction with the WebShop environment.
"""

import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_basic_import():
    """Test if webshop_minimal can be imported"""
    print("=" * 60)
    print("Test 1: Importing WebShop modules")
    print("=" * 60)
    try:
        from webshop_minimal import WebAgentTextEnv, init_basedir
        print("✓ Successfully imported WebShop modules")
        return True, WebAgentTextEnv, init_basedir
    except ImportError as e:
        print(f"✗ Failed to import: {e}")
        return False, None, None

def test_environment_creation(WebAgentTextEnv, init_basedir, dataset="small"):
    """Test environment creation and initialization"""
    print("\n" + "=" * 60)
    print(f"Test 2: Creating WebShop environment (dataset: {dataset})")
    print("=" * 60)
    try:
        init_basedir(dataset)
        print(f"✓ Initialized base directory for {dataset} dataset")

        env = WebAgentTextEnv()
        print("✓ Successfully created WebAgentTextEnv instance")
        return True, env
    except Exception as e:
        print(f"✗ Failed to create environment: {e}")
        return False, None

def test_environment_reset(env):
    """Test environment reset"""
    print("\n" + "=" * 60)
    print("Test 3: Resetting environment")
    print("=" * 60)
    try:
        obs = env.reset(session=0)
        print("✓ Successfully reset environment")
        print(f"\nInitial observation (first 500 chars):")
        print("-" * 60)
        print(obs[:500])
        if len(obs) > 500:
            print(f"... ({len(obs) - 500} more characters)")
        print("-" * 60)
        return True, obs
    except Exception as e:
        print(f"✗ Failed to reset: {e}")
        return False, None

def test_environment_step(env):
    """Test taking a step in the environment"""
    print("\n" + "=" * 60)
    print("Test 4: Taking a step in the environment")
    print("=" * 60)
    try:
        # Try a search action
        action = "search[laptop]"
        print(f"Action: {action}")

        obs, reward, done, info = env.step(action)
        print(f"✓ Step successful")
        print(f"Reward: {reward}")
        print(f"Done: {done}")
        print(f"\nNew observation (first 500 chars):")
        print("-" * 60)
        print(obs[:500])
        if len(obs) > 500:
            print(f"... ({len(obs) - 500} more characters)")
        print("-" * 60)
        return True
    except Exception as e:
        print(f"✗ Failed to step: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ragen_integration():
    """Test RAGEN environment wrapper"""
    print("\n" + "=" * 60)
    print("Test 5: Testing RAGEN WebShop integration")
    print("=" * 60)
    try:
        from ragen.env.webshop.env import WebShopEnv
        from ragen.env.webshop.config import WebShopEnvConfig

        print("✓ Successfully imported RAGEN WebShop modules")

        config = WebShopEnvConfig(dataset="small")
        env = WebShopEnv(config=config)
        print("✓ Successfully created RAGEN WebShopEnv instance")

        # Test reset with seed
        obs = env.reset(seed=42, mode="train")
        print("✓ Successfully reset with seed")
        print(f"\nRAGEN environment observation (first 300 chars):")
        print("-" * 60)
        print(str(obs)[:300])
        print("-" * 60)

        return True
    except Exception as e:
        print(f"✗ Failed RAGEN integration test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_availability(dataset="small"):
    """Test if required data files exist"""
    print("\n" + "=" * 60)
    print(f"Test 6: Checking data availability ({dataset})")
    print("=" * 60)

    data_dir = f"external/webshop-minimal/webshop_minimal/data/{dataset}"

    if not os.path.exists(data_dir):
        print(f"✗ Data directory not found: {data_dir}")
        return False

    print(f"✓ Data directory exists: {data_dir}")

    # List files in the directory
    try:
        files = os.listdir(data_dir)
        print(f"\nFiles in {dataset} dataset:")
        for f in files:
            file_path = os.path.join(data_dir, f)
            size = os.path.getsize(file_path) if os.path.isfile(file_path) else "N/A"
            print(f"  - {f} ({size} bytes)")
        return True
    except Exception as e:
        print(f"✗ Failed to list data files: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RAGEN WebShop Environment Test Suite")
    print("=" * 60)

    results = []

    # Test 1: Import
    success, WebAgentTextEnv, init_basedir = test_basic_import()
    results.append(("Import modules", success))
    if not success:
        print("\n✗ Cannot proceed without successful import")
        print_summary(results)
        return

    # Test 6: Data availability
    success = test_data_availability("small")
    results.append(("Data availability", success))

    # Test 2: Environment creation
    success, env = test_environment_creation(WebAgentTextEnv, init_basedir)
    results.append(("Create environment", success))
    if not success:
        print_summary(results)
        return

    # Test 3: Environment reset
    success, obs = test_environment_reset(env)
    results.append(("Reset environment", success))

    # Test 4: Environment step
    if success:
        success = test_environment_step(env)
        results.append(("Take step", success))

    # Test 5: RAGEN integration
    success = test_ragen_integration()
    results.append(("RAGEN integration", success))

    # Print summary
    print_summary(results)

def print_summary(results):
    """Print test summary"""
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")

    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! WebShop environment is ready.")
        print("\nYou can now start training with:")
        print("  python train.py --config-name _6_webshop")
        print("\nOr use the quick start script:")
        print("  bash scripts/quick_start_webshop.sh")
    else:
        print("\n⚠️  Some tests failed. Please check the setup.")
        print("\nTo set up WebShop, run:")
        print("  bash scripts/setup_webshop.sh")

    print("=" * 60)

if __name__ == "__main__":
    main()
