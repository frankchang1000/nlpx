#!/usr/bin/env python3
"""
Reddit Personality Generator
Uses GPT-5-nano to extract distinct user personalities from Reddit posts.
"""

import csv
import json
import random
import time
from collections import defaultdict, Counter
from typing import List, Dict, Tuple
import os
from openai import OpenAI

class PersonalityGenerator:
    def __init__(self, api_key: str = None):
        """Initialize the personality generator with OpenAI client."""
        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()
        self.posts_data = []
        self.generated_personalities = []
        
    def load_reddit_data(self, csv_path: str):
        """Load Reddit posts from CSV file."""
        print("📚 Loading Reddit data...")
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.posts_data = list(reader)
        
        print(f"✅ Loaded {len(self.posts_data)} posts from {len(set(p['subreddit'] for p in self.posts_data))} subreddits")
    
    def group_posts_by_strategy(self, strategy: str = "mixed") -> List[Dict]:
        """
        Group posts using different strategies for personality generation.
        
        Strategies:
        - 'subreddit': Group by subreddit (community-based personalities)
        - 'length': Group by post length (detailed vs brief communicators)  
        - 'mixed': Combine multiple posts from different contexts
        - 'individual': Each substantial post becomes a personality
        """
        groups = []
        
        if strategy == "subreddit":
            # Group by subreddit, focusing on active communities
            subreddit_posts = defaultdict(list)
            for post in self.posts_data:
                if post['subreddit'] != 'unknown':
                    subreddit_posts[post['subreddit']].append(post)
            
            # Only use subreddits with multiple posts for richer personalities
            for subreddit, posts in subreddit_posts.items():
                if len(posts) >= 2:  # At least 2 posts for personality depth
                    # Limit to top 5 posts by word count for API efficiency
                    top_posts = sorted(posts, key=lambda x: int(x['word_count']), reverse=True)[:5]
                    groups.append({
                        'type': 'subreddit',
                        'identifier': subreddit,
                        'posts': top_posts,
                        'total_words': sum(int(p['word_count']) for p in top_posts)
                    })
        
        elif strategy == "individual":
            # Each substantial post becomes its own personality
            substantial_posts = [p for p in self.posts_data if int(p['word_count']) >= 200]
            for post in substantial_posts:
                groups.append({
                    'type': 'individual',
                    'identifier': f"{post['subreddit']}_{post['post_id']}",
                    'posts': [post],
                    'total_words': int(post['word_count'])
                })
        
        elif strategy == "mixed":
            # Create diverse personality profiles by mixing posts from different contexts
            # This creates more complex, multi-faceted personalities
            
            # Categorize posts by themes
            mental_health = ['depression', 'anxiety', 'BPD', 'OCD', 'bipolar', 'autism', 'ADHD']
            relationships = ['relationship_advice', 'dating_advice', 'Marriage', 'relationships']
            lifestyle = ['stopdrinking', 'NoFap', 'fitness', 'weed', 'whiskey']
            advice = ['AmItheAsshole', 'AITAH', 'legaladvice', 'personalfinance']
            personal = ['offmychest', 'TrueOffMyChest', 'confessions', 'Vent']
            
            theme_groups = {
                'mental_health': mental_health,
                'relationships': relationships, 
                'lifestyle': lifestyle,
                'advice_seeking': advice,
                'personal_sharing': personal
            }
            
            # Group posts by themes
            themed_posts = defaultdict(list)
            for post in self.posts_data:
                subreddit = post['subreddit']
                for theme, subreddits in theme_groups.items():
                    if subreddit in subreddits:
                        themed_posts[theme].append(post)
                        break
                else:
                    themed_posts['other'].append(post)
            
            # Create mixed personalities by combining 2-4 posts from different themes
            used_posts = set()
            for i in range(50):  # Generate 50 mixed personalities
                available_themes = [t for t in themed_posts.keys() if len(themed_posts[t]) > 0]
                if len(available_themes) < 2:
                    break
                
                # Select 2-3 themes randomly
                selected_themes = random.sample(available_themes, min(3, len(available_themes)))
                mixed_posts = []
                
                for theme in selected_themes:
                    # Get unused posts from this theme
                    available_posts = [p for p in themed_posts[theme] 
                                     if p['post_id'] not in used_posts and int(p['word_count']) >= 100]
                    if available_posts:
                        post = random.choice(available_posts)
                        mixed_posts.append(post)
                        used_posts.add(post['post_id'])
                
                if len(mixed_posts) >= 2:
                    groups.append({
                        'type': 'mixed',
                        'identifier': f"mixed_personality_{i+1}",
                        'posts': mixed_posts,
                        'total_words': sum(int(p['word_count']) for p in mixed_posts),
                        'themes': selected_themes
                    })
        
        elif strategy == "length":
            # Group by communication style (brief vs detailed)
            brief_posts = [p for p in self.posts_data if 50 <= int(p['word_count']) <= 200]
            detailed_posts = [p for p in self.posts_data if int(p['word_count']) >= 500]
            
            # Create brief communicator personalities (combine multiple short posts)
            random.shuffle(brief_posts)
            for i in range(0, min(len(brief_posts), 100), 5):  # Groups of 5 brief posts
                group_posts = brief_posts[i:i+5]
                if len(group_posts) >= 3:
                    groups.append({
                        'type': 'brief_communicator',
                        'identifier': f"brief_comm_{i//5 + 1}",
                        'posts': group_posts,
                        'total_words': sum(int(p['word_count']) for p in group_posts)
                    })
            
            # Detailed communicator personalities (1-2 long posts each)
            for i, post in enumerate(detailed_posts[:30]):  # Top 30 detailed posts
                groups.append({
                    'type': 'detailed_communicator', 
                    'identifier': f"detailed_comm_{i+1}",
                    'posts': [post],
                    'total_words': int(post['word_count'])
                })
        
        print(f"📊 Created {len(groups)} personality groups using '{strategy}' strategy")
        return groups
    
    def create_personality_prompt(self, group: Dict) -> str:
        """Create a detailed prompt for GPT-5-nano to extract personality traits."""
        
        # Combine all post texts
        combined_text = "\n\n---POST SEPARATOR---\n\n".join([post['full_text'] for post in group['posts']])
        
        # Truncate if too long (GPT-5-nano likely has token limits)
        if len(combined_text) > 8000:  # Rough character limit
            combined_text = combined_text[:8000] + "...[truncated]"
        
        prompt = f"""Analyze the following Reddit post(s) and extract a detailed personality profile for the author. Focus on creating a specific, nuanced character that could be used in a simulation.

REDDIT POSTS:
{combined_text}

Extract the following personality dimensions:

**CORE TRAITS** (3-5 key personality characteristics):
- Use specific adjectives (e.g., "methodical and detail-oriented" not just "organized")

**COMMUNICATION STYLE**:
- How they express themselves (formal/casual, direct/indirect, emotional/logical)
- Typical language patterns or phrases they might use

**INTERESTS & HOBBIES**:
- What they're passionate about
- How they spend their free time
- Level of expertise in their interests

**SOCIAL BEHAVIOR**:
- How they interact with others
- Comfort level in social situations
- Relationship patterns

**EMOTIONAL PATTERNS**:
- How they handle stress, conflict, or challenges
- What motivates them
- Common emotional responses

**LIFESTYLE & HABITS**:
- Daily routines or preferences
- Living situation preferences
- Work/life balance approach

**BACKGROUND HINTS**:
- Approximate age range and life stage
- Possible education/career background
- Cultural or regional influences

**UNIQUE QUIRKS**:
- Specific behaviors, preferences, or viewpoints that make them distinctive
- Any notable contradictions or complexities

Create a cohesive personality that feels like a real person with depth, contradictions, and specific details. Focus on traits that would affect how they behave in social situations and make decisions.

Respond in JSON format with clear categories."""

        return prompt
    
    def _process_personality_fields(self, personality_data: Dict):
        """Process parsed personality into easy-to-use fields for random selection."""
        parsed = personality_data.get('parsed_personality')
        if not parsed:
            return
        
        try:
            # Extract core traits as flat list (GPT-5-nano uses uppercase keys)
            core_traits = parsed.get('CORE_TRAITS', []) or parsed.get('core_traits', [])
            if isinstance(core_traits, list):
                personality_data['core_traits_list'] = core_traits
            elif isinstance(core_traits, str):
                personality_data['core_traits_list'] = [t.strip() for t in core_traits.split(',')]
            
            # Extract interests as flat list
            interests_hobbies = parsed.get('INTERESTS_HOBBIES', {}) or parsed.get('interests_hobbies', {})
            interests = []
            if isinstance(interests_hobbies, dict):
                interests.extend(interests_hobbies.get('passions', []))
                interests.extend(interests_hobbies.get('spend_time', []))
            elif isinstance(interests_hobbies, list):
                interests = interests_hobbies
            personality_data['interests_list'] = interests
            
            # Create personality summary (first 200 chars of description)
            summary_sources = [
                parsed.get('summary', ''),
                parsed.get('description', ''),
                ', '.join(personality_data['core_traits_list'][:3])
            ]
            summary = next((s for s in summary_sources if s), 'No summary available')
            personality_data['personality_summary'] = summary[:200] + ('...' if len(summary) > 200 else '')
            
            # Extract age range
            background = parsed.get('BACKGROUND_HINTS', {}) or parsed.get('background_hints', '')
            age_text = ''
            if isinstance(background, dict):
                age_text = background.get('approx_age_range', '') or background.get('age_range', '')
            else:
                age_text = str(background)
            
            if '15-18' in age_text or 'teen' in age_text.lower() or 'high school' in age_text.lower():
                personality_data['age_range'] = '15-18'
            elif '18-22' in age_text or 'college' in age_text.lower():
                personality_data['age_range'] = '18-22'
            elif '20-25' in age_text or '20' in age_text:
                personality_data['age_range'] = '20-25'
            elif '25-35' in age_text or '30' in age_text or 'career' in age_text.lower():
                personality_data['age_range'] = '25-35'
            elif '35-45' in age_text or '40' in age_text or 'middle' in age_text.lower():
                personality_data['age_range'] = '35-45'
            else:
                personality_data['age_range'] = 'unknown'
            
            # Determine social level
            traits_text = ' '.join(personality_data['core_traits_list']).lower()
            social_behavior = parsed.get('SOCIAL_BEHAVIOR', {}) or parsed.get('social_behavior', {})
            social_text = ''
            if isinstance(social_behavior, dict):
                social_text = str(social_behavior.get('interaction_style', '')) + ' ' + str(social_behavior.get('comfort_in_social_situations', ''))
            else:
                social_text = str(social_behavior)
            combined_social = traits_text + ' ' + social_text.lower()
            
            if any(word in combined_social for word in ['shy', 'introverted', 'anxious', 'withdrawn', 'quiet']):
                personality_data['social_level'] = 'introvert'
            elif any(word in combined_social for word in ['outgoing', 'extroverted', 'social', 'talkative', 'gregarious']):
                personality_data['social_level'] = 'extrovert'
            else:
                personality_data['social_level'] = 'ambivert'
            
            # Create searchable tags
            tags = set()
            tags.update(personality_data['subreddits'])
            tags.update([t.lower().replace(' ', '_') for t in personality_data['core_traits_list']])
            tags.update([i.lower().replace(' ', '_') for i in personality_data['interests_list']])
            tags.add(personality_data['social_level'])
            tags.add(personality_data['age_range'])
            personality_data['personality_tags'] = list(tags)
            
            # Calculate complexity score (1-5)
            complexity = 1
            if len(personality_data['core_traits_list']) >= 4:
                complexity += 1
            if len(personality_data['interests_list']) >= 3:
                complexity += 1
            if len(personality_data['subreddits']) >= 3:
                complexity += 1
            if parsed.get('unique_quirks') or parsed.get('contradictions'):
                complexity += 1
            personality_data['complexity_score'] = min(complexity, 5)
            
            # Suggest suitable roles based on traits and interests
            roles = []
            interests_lower = [i.lower() for i in personality_data['interests_list']]
            traits_lower = [t.lower() for t in personality_data['core_traits_list']]
            
            if any(word in interests_lower for word in ['whiskey', 'alcohol', 'drinking', 'bar']):
                roles.append('whiskey_enthusiast')
            if any(word in interests_lower for word in ['fitness', 'gym', 'exercise', 'sports']):
                roles.append('fitness_enthusiast')
            if any(word in traits_lower for word in ['analytical', 'logical', 'methodical']):
                roles.append('analyst_type')
            if any(word in traits_lower for word in ['creative', 'artistic', 'imaginative']):
                roles.append('creative_type')
            if any(word in interests_lower for word in ['gaming', 'streaming', 'twitch']):
                roles.append('gamer_streamer')
            if any(word in traits_lower for word in ['helpful', 'caring', 'supportive']):
                roles.append('helper_type')
            
            personality_data['suitable_for_roles'] = roles
            
        except Exception as e:
            print(f"    ⚠️ Error processing personality fields: {e}")
    
    def generate_personality_batch(self, groups: List[Dict], batch_size: int = 5, delay: float = 1.0) -> List[Dict]:
        """Generate personalities in batches to manage API rate limits."""
        personalities = []
        
        print(f"🤖 Generating personalities for {len(groups)} groups...")
        print(f"📦 Processing in batches of {batch_size} with {delay}s delay")
        
        for i in range(0, len(groups), batch_size):
            batch = groups[i:i+batch_size]
            print(f"\n🔄 Processing batch {i//batch_size + 1}/{(len(groups)-1)//batch_size + 1}")
            
            for j, group in enumerate(batch):
                try:
                    print(f"  • Generating personality {i+j+1}: {group['identifier']} ({group['total_words']} words)")
                    
                    prompt = self.create_personality_prompt(group)
                    
                    # Call GPT-5-nano
                    result = self.client.responses.create(
                        model="gpt-5-nano",
                        input=prompt,
                        reasoning={"effort": "medium"},
                        text={"verbosity": "medium"}
                    )
                    
                    # Parse the response
                    personality_data = {
                        'id': f"personality_{i+j+1:03d}",
                        'source_type': group['type'],
                        'source_identifier': group['identifier'],
                        'source_posts': len(group['posts']),
                        'source_words': group['total_words'],
                        'raw_response': result.output_text,
                        'subreddits': list(set(p['subreddit'] for p in group['posts'])),
                        'post_ids': [p['post_id'] for p in group['posts']],
                        # Fields for easy random selection
                        'personality_summary': '',  # Will be filled after parsing
                        'core_traits_list': [],     # Flat list for easy filtering
                        'interests_list': [],       # Flat list for easy filtering
                        'age_range': '',           # e.g., "20-25", "30-35"
                        'likely_gender': '',       # if determinable
                        'occupation_hints': [],    # job/career indicators
                        'personality_tags': [],    # searchable tags
                        'complexity_score': 0,     # 1-5 scale
                        'social_level': '',        # introvert/ambivert/extrovert
                        'suitable_for_roles': []   # suggested character roles
                    }
                    
                    # Try to parse JSON from response
                    try:
                        # Look for JSON in the response
                        response_text = result.output_text
                        if '{' in response_text and '}' in response_text:
                            json_start = response_text.find('{')
                            json_end = response_text.rfind('}') + 1
                            json_str = response_text[json_start:json_end]
                            personality_data['parsed_personality'] = json.loads(json_str)
                            
                            # Process into easy-to-use fields
                            self._process_personality_fields(personality_data)
                        else:
                            personality_data['parsed_personality'] = None
                    except json.JSONDecodeError:
                        personality_data['parsed_personality'] = None
                        print(f"    ⚠️ Could not parse JSON from response")
                    
                    personalities.append(personality_data)
                    
                except Exception as e:
                    print(f"    ❌ Error generating personality for {group['identifier']}: {e}")
                    continue
                
                # Rate limiting delay
                time.sleep(delay)
            
            print(f"✅ Completed batch {i//batch_size + 1}")
        
        print(f"\n🎉 Generated {len(personalities)} personalities total")
        return personalities
    
    def save_personalities(self, personalities: List[Dict], output_path: str):
        """Save generated personalities to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(personalities, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(personalities)} personalities to {output_path}")
    
    def create_personality_browser_csv(self, personalities: List[Dict], output_path: str):
        """Create a CSV file optimized for browsing and random selection of personalities."""
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'id', 'personality_summary', 'core_traits', 'interests', 
                'age_range', 'social_level', 'complexity_score', 'suitable_roles',
                'source_type', 'subreddits', 'tags', 'source_words'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for p in personalities:
                if p.get('parsed_personality'):  # Only include successfully parsed personalities
                    writer.writerow({
                        'id': p['id'],
                        'personality_summary': p.get('personality_summary', ''),
                        'core_traits': '; '.join(p.get('core_traits_list', [])),
                        'interests': '; '.join(p.get('interests_list', [])),
                        'age_range': p.get('age_range', ''),
                        'social_level': p.get('social_level', ''),
                        'complexity_score': p.get('complexity_score', 0),
                        'suitable_roles': '; '.join(p.get('suitable_for_roles', [])),
                        'source_type': p['source_type'],
                        'subreddits': '; '.join(p['subreddits']),
                        'tags': '; '.join(p.get('personality_tags', [])),
                        'source_words': p['source_words']
                    })
        
        print(f"📊 Created personality browser CSV: {output_path}")
    
    def create_random_selector_functions(self, personalities: List[Dict]) -> str:
        """Create helper functions for random personality selection."""
        
        # Filter only successfully parsed personalities
        valid_personalities = [p for p in personalities if p.get('parsed_personality')]
        
        selector_code = f'''
# PERSONALITY RANDOM SELECTOR FUNCTIONS
# Generated from {len(valid_personalities)} personalities

import random
import json

def load_personalities(json_path):
    """Load personalities from JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)

def random_personality(personalities, filters=None):
    """
    Get a random personality with optional filters.
    
    filters example:
    {{
        'social_level': 'introvert',
        'age_range': '20-25', 
        'suitable_roles': ['whiskey_enthusiast'],
        'complexity_score': [4, 5],  # list means "any of these values"
        'tags': ['depression', 'anxiety']  # must contain ANY of these tags
    }}
    """
    candidates = personalities
    
    if filters:
        for key, value in filters.items():
            if key == 'complexity_score' and isinstance(value, list):
                candidates = [p for p in candidates if p.get(key, 0) in value]
            elif key == 'suitable_roles' and isinstance(value, list):
                candidates = [p for p in candidates if any(role in p.get(key, []) for role in value)]
            elif key == 'tags' and isinstance(value, list):
                candidates = [p for p in candidates if any(tag in p.get('personality_tags', []) for tag in value)]
            else:
                candidates = [p for p in candidates if p.get(key) == value]
    
    return random.choice(candidates) if candidates else None

def get_personalities_by_role(personalities, role):
    """Get all personalities suitable for a specific role."""
    return [p for p in personalities if role in p.get('suitable_for_roles', [])]

def get_diverse_set(personalities, count=3):
    """Get a diverse set of personalities with different traits."""
    if len(personalities) < count:
        return personalities
    
    selected = []
    used_traits = set()
    
    # First, try to get personalities with different core traits
    for p in personalities:
        if len(selected) >= count:
            break
        
        p_traits = set(p.get('core_traits_list', []))
        if not p_traits.intersection(used_traits):
            selected.append(p)
            used_traits.update(p_traits)
    
    # Fill remaining slots randomly
    remaining = [p for p in personalities if p not in selected]
    while len(selected) < count and remaining:
        selected.append(random.choice(remaining))
        remaining.remove(selected[-1])
    
    return selected

# EXAMPLE USAGE:
# personalities = load_personalities('all_personalities.json')
# 
# # Get a random whiskey enthusiast
# whiskey_person = random_personality(personalities, {{'suitable_roles': ['whiskey_enthusiast']}})
# 
# # Get an introverted young adult
# introvert = random_personality(personalities, {{'social_level': 'introvert', 'age_range': '20-25'}})
# 
# # Get 3 diverse personalities
# diverse_group = get_diverse_set(personalities, 3)

# AVAILABLE FILTERS:
# - social_level: {set(p.get('social_level', '') for p in valid_personalities)}
# - age_range: {set(p.get('age_range', '') for p in valid_personalities)}
# - complexity_score: {set(p.get('complexity_score', 0) for p in valid_personalities)}
# - suitable_roles: {set(role for p in valid_personalities for role in p.get('suitable_for_roles', []))}
# - source_type: {set(p.get('source_type', '') for p in valid_personalities)}
'''
        
        return selector_code
    
    def create_personality_summary(self, personalities: List[Dict]) -> str:
        """Create a summary report of generated personalities."""
        total = len(personalities)
        parsed = sum(1 for p in personalities if p.get('parsed_personality'))
        
        # Analyze source types
        source_types = Counter(p['source_type'] for p in personalities)
        
        # Analyze subreddit diversity
        all_subreddits = set()
        for p in personalities:
            all_subreddits.update(p['subreddits'])
        
        summary = f"""
🎭 PERSONALITY GENERATION SUMMARY
{'='*50}

📊 STATISTICS:
• Total personalities generated: {total}
• Successfully parsed JSON: {parsed} ({parsed/total*100:.1f}%)
• Unique source subreddits: {len(all_subreddits)}
• Average words per personality: {sum(p['source_words'] for p in personalities)/total:.0f}

📈 SOURCE TYPE BREAKDOWN:
"""
        for source_type, count in source_types.most_common():
            summary += f"• {source_type}: {count} personalities\n"
        
        summary += f"""
🌍 TOP SUBREDDITS REPRESENTED:
"""
        subreddit_counts = Counter()
        for p in personalities:
            for sub in p['subreddits']:
                subreddit_counts[sub] += 1
        
        for subreddit, count in subreddit_counts.most_common(15):
            summary += f"• r/{subreddit}: {count} personalities\n"
        
        return summary

def main():
    """Main execution function - DO NOT RUN YET"""
    # Configuration
    INPUT_CSV = '/Users/frankchang/Desktop/code/nlpx/scripting/reddit_posts_clean.csv'
    OUTPUT_DIR = '/Users/frankchang/Desktop/code/nlpx/scripting/personalities'
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Initialize generator
    generator = PersonalityGenerator()
    
    # Load data
    generator.load_reddit_data(INPUT_CSV)
    
    # Generate personalities using different strategies
    strategies = ['mixed', 'subreddit', 'individual', 'length']
    
    all_personalities = []
    
    for strategy in strategies:
        print(f"\n🎯 Using strategy: {strategy}")
        groups = generator.group_posts_by_strategy(strategy)
        
        # Limit groups per strategy to manage costs
        max_groups = {'mixed': 30, 'subreddit': 20, 'individual': 25, 'length': 15}
        groups = groups[:max_groups.get(strategy, 20)]
        
        personalities = generator.generate_personality_batch(
            groups, 
            batch_size=3,  # Small batches to be safe
            delay=2.0      # 2 second delay between calls
        )
        
        # Save strategy-specific results
        strategy_output = os.path.join(OUTPUT_DIR, f'personalities_{strategy}.json')
        generator.save_personalities(personalities, strategy_output)
        
        all_personalities.extend(personalities)
    
    # Save combined results
    combined_output = os.path.join(OUTPUT_DIR, 'all_personalities.json')
    generator.save_personalities(all_personalities, combined_output)
    
    # Create personality browser CSV for easy random selection
    browser_csv = os.path.join(OUTPUT_DIR, 'personality_browser.csv')
    generator.create_personality_browser_csv(all_personalities, browser_csv)
    
    # Create random selector helper functions
    selector_code = generator.create_random_selector_functions(all_personalities)
    selector_output = os.path.join(OUTPUT_DIR, 'personality_selector.py')
    with open(selector_output, 'w') as f:
        f.write(selector_code)
    print(f"🎲 Created random selector functions: {selector_output}")
    
    # Create summary report
    summary = generator.create_personality_summary(all_personalities)
    summary_output = os.path.join(OUTPUT_DIR, 'generation_summary.txt')
    with open(summary_output, 'w') as f:
        f.write(summary)
    
    print(summary)
    print(f"\n🎉 COMPLETE! Check {OUTPUT_DIR} for all generated personalities.")
    print(f"\n📋 FILES CREATED:")
    print(f"   • all_personalities.json - Full personality data")
    print(f"   • personality_browser.csv - Easy browsing/filtering")
    print(f"   • personality_selector.py - Random selection functions")
    print(f"   • generation_summary.txt - Statistics and overview")
    print(f"\n🎯 QUICK START:")
    print(f"   1. Open personality_browser.csv to browse personalities")
    print(f"   2. Use personality_selector.py for random selection")
    print(f"   3. Filter by: age_range, social_level, interests, roles, etc.")

if __name__ == "__main__":
    print("⚠️  This script is ready but not executed yet.")
    print("📝 Review the code and configuration before running.")
    print("💰 Remember: This will make many API calls to GPT-5-nano!")
    print("\n🚀 To run: python3 generate_personalities.py")
    # Uncomment the next line when ready to execute
    # main()
