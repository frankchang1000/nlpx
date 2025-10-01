#!/usr/bin/env python3
"""
Reddit CoNLL Format Parser
Extracts clean text from CoNLL-formatted Reddit posts and outputs to CSV.
"""

import csv
import re
from typing import List, Dict, Tuple
from urllib.parse import urlparse
import os

def extract_subreddit_from_url(url: str) -> str:
    """Extract subreddit name from Reddit URL."""
    try:
        # Extract subreddit from URL like: https://www.reddit.com/r/stopdrinking/comments/...
        match = re.search(r'/r/([^/]+)/', url)
        return match.group(1) if match else 'unknown'
    except:
        return 'unknown'

def extract_post_id_from_url(url: str) -> str:
    """Extract post ID from Reddit URL."""
    try:
        # Extract post ID from URL like: .../comments/10003oj/...
        match = re.search(r'/comments/([^/]+)/', url)
        return match.group(1) if match else 'unknown'
    except:
        return 'unknown'

def parse_conll_file(file_path: str) -> List[Dict]:
    """
    Parse CoNLL format file and extract clean text posts.
    
    Returns:
        List of dictionaries with post information
    """
    posts = []
    current_post = None
    current_section_words = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check if this is a new post (starts with https://)
            if line.startswith('https://'):
                # Save previous post if exists
                if current_post and current_section_words:
                    current_post['sections'].append(' '.join(current_section_words))
                    current_section_words = []
                
                if current_post:
                    # Combine all sections into full text
                    current_post['full_text'] = ' '.join(current_post['sections'])
                    posts.append(current_post)
                
                # Start new post
                url_parts = line.split(' ')
                url = url_parts[0]
                
                current_post = {
                    'post_id': extract_post_id_from_url(url),
                    'subreddit': extract_subreddit_from_url(url),
                    'url': url,
                    'sections': [],
                    'full_text': '',
                    'line_start': line_num
                }
                current_section_words = []
                continue
            
            # Check for section separator
            if line == '[SEP]':
                if current_section_words:
                    current_post['sections'].append(' '.join(current_section_words))
                    current_section_words = []
                continue
            
            # Parse word and label
            if ' ' in line:
                parts = line.rsplit(' ', 1)  # Split from right to handle words with spaces
                if len(parts) == 2:
                    word, label = parts
                    # Only keep the word, ignore the label
                    current_section_words.append(word)
            else:
                # Handle lines that might not have labels (shouldn't happen in proper CoNLL)
                current_section_words.append(line)
    
    # Don't forget the last post
    if current_post:
        if current_section_words:
            current_post['sections'].append(' '.join(current_section_words))
        current_post['full_text'] = ' '.join(current_post['sections'])
        posts.append(current_post)
    
    return posts

def save_to_csv(posts: List[Dict], output_path: str):
    """Save parsed posts to CSV file."""
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['post_id', 'subreddit', 'url', 'section_count', 'word_count', 'full_text']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for post in posts:
            writer.writerow({
                'post_id': post['post_id'],
                'subreddit': post['subreddit'],
                'url': post['url'],
                'section_count': len(post['sections']),
                'word_count': len(post['full_text'].split()),
                'full_text': post['full_text']
            })

def save_sections_to_csv(posts: List[Dict], output_path: str):
    """Save individual sections to CSV file (one row per section)."""
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['post_id', 'subreddit', 'section_index', 'section_text', 'word_count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for post in posts:
            for i, section in enumerate(post['sections']):
                writer.writerow({
                    'post_id': post['post_id'],
                    'subreddit': post['subreddit'],
                    'section_index': i,
                    'section_text': section,
                    'word_count': len(section.split())
                })

def main():
    input_file = '/Users/frankchang/Desktop/code/nlpx/scripting/batch-1-conll-format.txt'
    output_dir = '/Users/frankchang/Desktop/code/nlpx/scripting'
    
    print("🔍 Parsing CoNLL format Reddit posts...")
    posts = parse_conll_file(input_file)
    
    print(f"✅ Parsed {len(posts)} posts")
    
    # Calculate some statistics
    total_words = sum(len(post['full_text'].split()) for post in posts)
    total_sections = sum(len(post['sections']) for post in posts)
    subreddits = set(post['subreddit'] for post in posts)
    
    print(f"📊 Statistics:")
    print(f"   • Total posts: {len(posts)}")
    print(f"   • Total sections: {total_sections}")
    print(f"   • Total words: {total_words:,}")
    print(f"   • Unique subreddits: {len(subreddits)}")
    print(f"   • Subreddits: {', '.join(sorted(subreddits))}")
    
    # Save full posts to CSV
    posts_output = os.path.join(output_dir, 'reddit_posts_clean.csv')
    save_to_csv(posts, posts_output)
    print(f"💾 Saved full posts to: {posts_output}")
    
    # Save individual sections to CSV
    sections_output = os.path.join(output_dir, 'reddit_sections_clean.csv')
    save_sections_to_csv(posts, sections_output)
    print(f"💾 Saved sections to: {sections_output}")
    
    # Show sample of first few posts
    print(f"\n📝 Sample posts:")
    for i, post in enumerate(posts[:3]):
        print(f"\n{i+1}. Post ID: {post['post_id']} (r/{post['subreddit']})")
        print(f"   Sections: {len(post['sections'])}, Words: {len(post['full_text'].split())}")
        print(f"   Text preview: {post['full_text'][:200]}...")

if __name__ == "__main__":
    main()
