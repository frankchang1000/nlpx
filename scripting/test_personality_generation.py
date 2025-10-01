#!/usr/bin/env python3
"""
Test script for personality generation - runs a small batch first
"""

import os
import sys
sys.path.append('/Users/frankchang/Desktop/code/nlpx/scripting')

from generate_personalities import PersonalityGenerator

def test_run():
    """Run a small test to verify everything works before full generation."""
    
    print("🧪 PERSONALITY GENERATION TEST RUN")
    print("="*50)
    
    # Configuration
    INPUT_CSV = '/Users/frankchang/Desktop/code/nlpx/scripting/reddit_posts_clean.csv'
    OUTPUT_DIR = '/Users/frankchang/Desktop/code/nlpx/scripting/test_personalities'
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Initialize generator
    generator = PersonalityGenerator()
    
    # Load data
    generator.load_reddit_data(INPUT_CSV)
    
    # Test with just one strategy and small batch
    print(f"\n🎯 Testing with 'mixed' strategy (5 personalities)")
    groups = generator.group_posts_by_strategy('mixed')
    
    # Limit to just 5 for testing
    test_groups = groups[:5]
    print(f"📦 Testing with {len(test_groups)} personality groups")
    
    # Generate personalities
    personalities = generator.generate_personality_batch(
        test_groups, 
        batch_size=2,  # Small batches
        delay=1.0      # 1 second delay
    )
    
    # Save test results
    test_output = os.path.join(OUTPUT_DIR, 'test_personalities.json')
    generator.save_personalities(personalities, test_output)
    
    # Create browser CSV
    browser_csv = os.path.join(OUTPUT_DIR, 'test_personality_browser.csv')
    generator.create_personality_browser_csv(personalities, browser_csv)
    
    # Create selector functions
    selector_code = generator.create_random_selector_functions(personalities)
    selector_output = os.path.join(OUTPUT_DIR, 'test_personality_selector.py')
    with open(selector_output, 'w') as f:
        f.write(selector_code)
    
    # Show results
    successful = sum(1 for p in personalities if p.get('parsed_personality'))
    print(f"\n✅ TEST RESULTS:")
    print(f"   • Generated: {len(personalities)} personalities")
    print(f"   • Successful: {successful} ({successful/len(personalities)*100:.1f}%)")
    print(f"   • Output directory: {OUTPUT_DIR}")
    
    if successful > 0:
        print(f"\n🎉 Test successful! Ready for full run.")
        print(f"📊 Check {browser_csv} to see the results")
        
        # Show a sample personality
        sample = next((p for p in personalities if p.get('parsed_personality')), None)
        if sample:
            print(f"\n📝 SAMPLE PERSONALITY:")
            print(f"   ID: {sample['id']}")
            print(f"   Summary: {sample.get('personality_summary', 'N/A')}")
            print(f"   Traits: {', '.join(sample.get('core_traits_list', []))}")
            print(f"   Interests: {', '.join(sample.get('interests_list', []))}")
            print(f"   Social Level: {sample.get('social_level', 'N/A')}")
            print(f"   Suitable Roles: {', '.join(sample.get('suitable_for_roles', []))}")
        
        return True
    else:
        print(f"\n❌ Test failed - no personalities successfully generated")
        print(f"🔍 Check the API key and GPT-5-nano availability")
        return False

if __name__ == "__main__":
    success = test_run()
    
    if success:
        print(f"\n🚀 READY FOR FULL RUN!")
        print(f"💰 Estimated cost for full run: ~90 API calls")
        print(f"⏱️  Estimated time: ~10-15 minutes")
        print(f"\n🔥 To run full generation:")
        print(f"   cd /Users/frankchang/Desktop/code/nlpx/scripting")
        print(f"   python3 -c \"from generate_personalities import *; main()\"")
    else:
        print(f"\n🛠️  Fix issues before running full generation")
