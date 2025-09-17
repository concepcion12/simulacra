#!/usr/bin/env python3
"""
Debug script to isolate import issues.
"""

def test_imports():
    print("Testing individual imports...")
    
    try:
        from simulacra.agents.behavioral_economics import (
            ProspectTheoryModule, TemporalDiscountingModule, DualProcessModule,
            GamblingBiasModule, HabitFormationModule, AddictionModule
        )
        print("✅ All behavioral economics imports successful")
    except Exception as e:
        print(f"❌ Behavioral economics import failed: {e}")
        
        # Test each one individually
        modules = [
            'ProspectTheoryModule', 'TemporalDiscountingModule', 'DualProcessModule',
            'GamblingBiasModule', 'HabitFormationModule', 'AddictionModule'
        ]
        
        for mod_name in modules:
            try:
                exec(f"from simulacra.agents.behavioral_economics import {mod_name}")
                print(f"✅ {mod_name} import successful")
            except Exception as e:
                print(f"❌ {mod_name} import failed: {e}")
        return
    
    try:
        from simulacra.agents.agent import Agent
        print("✅ Agent import successful")
    except Exception as e:
        print(f"❌ Agent import failed: {e}")
        return
        
    try:
        agent = Agent()
        print("✅ Agent creation successful")
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return

if __name__ == "__main__":
    test_imports() 
