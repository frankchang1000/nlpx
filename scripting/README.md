# Reddit Personality Generation Pipeline

A comprehensive system for extracting and generating diverse user personalities from Reddit CoNLL-format data using GPT-5-nano. Perfect for creating realistic character personalities for simulations, games, or research.

## 🎯 Overview

This pipeline transforms annotated Reddit posts into rich, detailed personality profiles that can be used to create diverse simulation characters. The system processes CoNLL-formatted Reddit data, extracts clean text, and uses GPT-5-nano to generate comprehensive personality profiles with traits, interests, communication styles, and behavioral patterns.

## 📁 Project Structure

```
scripting/
├── README.md                           # This file
├── batch-1-conll-format.txt           # Input: CoNLL-formatted Reddit data
├── parse_conll_reddit.py              # Step 1: Extract clean text from CoNLL
├── generate_personalities.py          # Step 2: Generate personalities with GPT-5-nano
├── test_personality_generation.py     # Test script for small batches
├── reddit_posts_clean.csv             # Output: Clean Reddit posts
├── reddit_sections_clean.csv          # Output: Individual post sections
├── test_personalities/                # Test output directory
│   ├── test_personalities.json        # Sample personality data
│   ├── test_personality_browser.csv   # Sample browsable format
│   └── test_personality_selector.py   # Sample selection functions
└── personalities/                     # Full output directory (when generated)
    ├── all_personalities.json         # Complete personality database
    ├── personality_browser.csv        # Easy browsing/filtering
    ├── personality_selector.py        # Random selection functions
    └── generation_summary.txt         # Statistics and overview
```

## 🚀 Quick Start

### Prerequisites

1. **Environment Setup**:
   ```bash
   conda activate nlpx
   # OpenAI library should already be installed
   ```

2. **API Key**: Ensure your OpenAI API key is configured for GPT-5-nano access

### Step-by-Step Usage

#### Step 1: Extract Clean Text from CoNLL Data

```bash
cd /Users/frankchang/Desktop/code/nlpx/scripting
python parse_conll_reddit.py
```

**What it does:**
- Parses `batch-1-conll-format.txt` (CoNLL-formatted Reddit posts)
- Removes all annotations (B-Health, I-Health, O, etc.)
- Extracts clean text and metadata
- Separates posts by URL boundaries and `[SEP]` markers

**Outputs:**
- `reddit_posts_clean.csv` - Full posts (558 posts, 175 subreddits)
- `reddit_sections_clean.csv` - Individual sections (11,992 sections)

#### Step 2: Test Personality Generation (Recommended)

```bash
python test_personality_generation.py
```

**What it does:**
- Runs a small test with 5 personalities
- Verifies GPT-5-nano API connectivity
- Shows sample output format
- Estimates costs for full run

**Outputs:**
- `test_personalities/` directory with sample results
- Success rate and quality assessment

#### Step 3: Generate Full Personality Database

```bash
python -c "from generate_personalities import *; main()"
```

**What it does:**
- Generates ~90 diverse personalities using 4 strategies
- Processes in batches with rate limiting
- Creates comprehensive personality profiles
- Estimated time: 10-15 minutes, ~90 API calls

**Outputs:**
- `personalities/all_personalities.json` - Complete database
- `personalities/personality_browser.csv` - Easy browsing
- `personalities/personality_selector.py` - Selection functions
- `personalities/generation_summary.txt` - Statistics

## 📊 Generated Data Structure

### Personality Profile Format

Each personality includes:

```json
{
  "id": "personality_001",
  "personality_summary": "Impulsive drama-prone teen with strong loyalty...",
  "core_traits_list": ["Impulsive", "Loyal-to-a-fault", "Emotionally reactive"],
  "interests_list": ["acting", "socializing", "online storytelling"],
  "age_range": "15-18",
  "social_level": "extrovert",
  "complexity_score": 4,
  "suitable_for_roles": ["creative_type", "helper_type"],
  "source_type": "mixed",
  "subreddits": ["AITAH", "depression", "relationships"],
  "personality_tags": ["drama", "loyal", "teen", "creative"],
  "parsed_personality": {
    "CORE_TRAITS": [...],
    "COMMUNICATION_STYLE": {...},
    "INTERESTS_HOBBIES": {...},
    "SOCIAL_BEHAVIOR": {...},
    "EMOTIONAL_PATTERNS": {...},
    "LIFESTYLE_HABITS": {...},
    "BACKGROUND_HINTS": {...},
    "UNIQUE_QUIRKS": [...]
  }
}
```

### Personality Generation Strategies

1. **Mixed Strategy** (30 personalities)
   - Combines 2-3 posts from different thematic areas
   - Creates complex, multi-faceted personalities
   - Themes: mental health, relationships, lifestyle, advice, personal

2. **Subreddit Strategy** (20 personalities)
   - Groups posts from same communities
   - Captures community-specific traits
   - Focus on active subreddits with multiple posts

3. **Individual Strategy** (25 personalities)
   - Each substantial post (200+ words) becomes a personality
   - Captures detailed individual expression styles
   - Deep dive into specific communication patterns

4. **Length Strategy** (15 personalities)
   - Brief communicators (combines 3-5 short posts)
   - Detailed communicators (1-2 long posts)
   - Captures different communication preferences

## 🎮 Using Generated Personalities

### Random Selection Examples

```python
# Load personalities
from personality_selector import *
personalities = load_personalities('all_personalities.json')

# Get a random whiskey enthusiast (perfect for your simulation!)
whiskey_char = random_personality(personalities, {
    'suitable_roles': ['whiskey_enthusiast'],
    'age_range': '25-35',
    'complexity_score': [4, 5]
})

# Get an introverted young adult
introvert = random_personality(personalities, {
    'social_level': 'introvert', 
    'age_range': '20-25'
})

# Get 3 diverse personalities for a simulation
diverse_trio = get_diverse_set(personalities, 3)

# Get someone with mental health themes
anxious_person = random_personality(personalities, {
    'tags': ['anxiety', 'depression']
})
```

### Available Filters

- **social_level**: `introvert`, `ambivert`, `extrovert`
- **age_range**: `15-18`, `18-22`, `20-25`, `25-35`, `35-45`
- **complexity_score**: `1-5` (personality depth)
- **suitable_roles**: `whiskey_enthusiast`, `fitness_enthusiast`, `gamer_streamer`, `analyst_type`, `creative_type`, `helper_type`
- **tags**: Any combination of subreddits, traits, interests
- **source_type**: `mixed`, `subreddit`, `individual`, `length`

### Browsing with CSV

Open `personality_browser.csv` in Excel/Google Sheets for easy visual browsing:
- Sort by complexity_score for depth
- Filter by age_range for demographics  
- Search interests for specific hobbies
- Filter by suitable_roles for character types

## 📈 Data Statistics

**Reddit Source Data:**
- 558 total posts from 175 unique subreddits
- 368,236 total words of clean text
- Average 659.9 words per post
- Diverse topics: mental health, relationships, hobbies, advice

**Generated Personalities:**
- ~90 total personalities (when full generation is run)
- 100% success rate in testing
- Rich, detailed profiles with contradictions and depth
- Suitable for character creation, research, or simulation

**Top Represented Communities:**
- Mental Health: depression, anxiety, BPD, OCD, autism
- Relationships: relationship_advice, dating_advice, Marriage
- Lifestyle: stopdrinking, whiskey, fitness, NoFap
- Advice: AmItheAsshole, legaladvice, personalfinance
- Personal: offmychest, confessions, TrueOffMyChest

## 🛠️ Customization

### Modifying Generation Strategies

Edit `generate_personalities.py` to:
- Adjust batch sizes and delays
- Modify personality grouping logic
- Change prompt templates
- Add new filtering criteria

### Adding New Data Sources

To process additional CoNLL data:
1. Place new `.txt` files in the scripting directory
2. Update `INPUT_CSV` path in scripts
3. Run the pipeline again

### Extending Personality Fields

Add new personality dimensions by:
1. Modifying the GPT-5-nano prompt in `create_personality_prompt()`
2. Updating `_process_personality_fields()` to extract new data
3. Adding fields to CSV output in `create_personality_browser_csv()`

## 🔧 Troubleshooting

**Common Issues:**

1. **OpenAI API Errors**
   - Verify API key is set correctly
   - Check GPT-5-nano model availability
   - Ensure sufficient API credits

2. **Empty Personality Fields**
   - Check if GPT-5-nano response format changed
   - Verify JSON parsing in `_process_personality_fields()`
   - Run test script to debug specific responses

3. **Rate Limiting**
   - Increase delay between API calls
   - Reduce batch sizes
   - Check OpenAI rate limits for your account

4. **Memory Issues**
   - Process smaller batches
   - Clear intermediate files
   - Monitor system memory usage

## 📝 File Descriptions

### Core Scripts

- **`parse_conll_reddit.py`**: CoNLL format parser and text extractor
- **`generate_personalities.py`**: Main personality generation system
- **`test_personality_generation.py`**: Small-scale testing script

### Output Files

- **`reddit_posts_clean.csv`**: Cleaned Reddit posts with metadata
- **`reddit_sections_clean.csv`**: Individual post sections
- **`all_personalities.json`**: Complete personality database
- **`personality_browser.csv`**: Human-readable personality browser
- **`personality_selector.py`**: Random selection utility functions

## 🎯 Use Cases

**Perfect for:**
- **Game Character Creation**: Generate diverse NPCs with realistic personalities
- **Simulation Agents**: Create believable agents for social simulations
- **Research**: Study personality patterns and communication styles
- **Creative Writing**: Develop complex, realistic characters
- **AI Training**: Generate diverse personality data for model training

**Character Types Available:**
- Whiskey enthusiasts (perfect for your current simulation!)
- Mental health advocates and strugglers
- Relationship advice seekers and givers
- Fitness and lifestyle enthusiasts
- Creative and artistic personalities
- Analytical and logical thinkers
- Social and extroverted types
- Introverted and anxious individuals

## 🚀 Next Steps

1. **Run the full generation** to create your complete personality database
2. **Integrate with your simulation** using the selection functions
3. **Customize personalities** for specific character needs
4. **Expand the dataset** with additional Reddit data
5. **Create character templates** for easy personality application

---

*Generated personalities are based on real Reddit posts but are anonymized and transformed for creative/research use. All personal information has been removed and personalities are fictional constructs.*
