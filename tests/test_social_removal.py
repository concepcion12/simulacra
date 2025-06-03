#!/usr/bin/env python3
"""
Test script to verify social components have been removed.
"""

def test_social_removal():
    """Test that social components are removed."""
    print("Testing social component removal...")
    
    # Test 1: ActionType.SOCIALIZE should not exist
    try:
        from src.utils.types import ActionType
        socialize_actions = [action for action in ActionType if 'SOCIAL' in action.name]
        if socialize_actions:
            print(f"❌ FAILED: Found social actions: {socialize_actions}")
            return False
        else:
            print("✅ PASSED: No SOCIALIZE action type found")
    except Exception as e:
        print(f"❌ FAILED: Error importing ActionType: {e}")
        return False
    
    # Test 2: SocializeOutcome should not exist
    try:
        from src.utils.types import SocializeOutcome
        print("❌ FAILED: SocializeOutcome still exists")
        return False
    except ImportError:
        print("✅ PASSED: SocializeOutcome successfully removed")
    except Exception as e:
        print(f"❌ FAILED: Unexpected error: {e}")
        return False
    
    # Test 3: Agent should not have social_connections
    try:
        from src.agents.agent import Agent
        agent = Agent()
        if hasattr(agent, 'social_connections'):
            print("❌ FAILED: Agent still has social_connections attribute")
            return False
        else:
            print("✅ PASSED: Agent.social_connections removed")
    except Exception as e:
        print(f"❌ FAILED: Error testing agent: {e}")
        return False
    
    # Test 4: UtilityWeights should not have social component
    try:
        from src.utils.types import UtilityWeights
        weights = UtilityWeights()
        if hasattr(weights, 'social'):
            print("❌ FAILED: UtilityWeights still has social component")
            return False
        else:
            print("✅ PASSED: UtilityWeights.social removed")
    except Exception as e:
        print(f"❌ FAILED: Error testing UtilityWeights: {e}")
        return False
    
    print("\n🎉 All tests passed! Social components successfully removed.")
    return True

if __name__ == "__main__":
    test_social_removal() 
