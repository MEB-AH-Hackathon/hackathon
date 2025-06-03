#!/usr/bin/env python3
"""
Create symptom mappings between VAERS symptoms and FDA adverse events
Using Claude API for intelligent matching
"""

import json
import random
import requests
import os
import time
from collections import Counter

def get_vaers_symptoms():
    """Extract, flatten, and dedupe symptoms from VAERS subset"""
    print("Loading VAERS symptoms...")
    
    with open('../json_data/vaers_subset.json', 'r') as f:
        vaers_data = json.load(f)
    
    print(f"Loaded {len(vaers_data)} VAERS reports")
    
    # Flatten all symptoms from all reports
    all_symptoms = []
    for record in vaers_data:
        symptom_list = record.get('symptom_list', [])
        if symptom_list:  # Make sure it's not empty
            all_symptoms.extend(symptom_list)
    
    print(f"Found {len(all_symptoms)} total symptom occurrences")
    
    # Count and dedupe
    symptom_counts = Counter(all_symptoms)
    print(f"Found {len(symptom_counts)} unique VAERS symptoms after deduping")
    
    # Show top symptoms
    print("Top 10 most common symptoms:")
    for symptom, count in symptom_counts.most_common(10):
        print(f"  {symptom}: {count:,}")
    
    # Sample for Claude API (limit to avoid too many API calls)
    all_symptoms_list = list(symptom_counts.keys())
    sample_size = min(500, len(all_symptoms_list))  # Limit to 500 for cost control
    sampled_symptoms = random.sample(all_symptoms_list, sample_size)
    
    print(f"\nSampled {len(sampled_symptoms)} symptoms for Claude mapping")
    
    return {symptom: symptom_counts[symptom] for symptom in sampled_symptoms}

def get_fda_adverse_events():
    """Extract all unique adverse events from FDA reports"""
    print("Loading FDA adverse events...")
    
    with open('../json_data/fda_reports.json', 'r') as f:
        fda_data = json.load(f)
    
    # Collect all adverse events from all vaccines
    all_adverse_events = set()
    for report in fda_data:
        adverse_events = report.get('adverse_events', [])
        all_adverse_events.update(adverse_events)
    
    fda_events = list(all_adverse_events)
    print(f"Found {len(fda_events)} unique FDA adverse events across all vaccines")
    
    return fda_events

def map_symptoms_with_claude(vaers_symptoms, fda_events):
    """Use Claude to map VAERS symptoms to FDA adverse events (can map to multiple)"""
    print("Starting Claude mapping process...")
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        return []
    
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        'x-api-key': api_key,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json'
    }
    
    # Create FDA events reference string
    fda_events_str = "\n".join([f"- {event}" for event in sorted(fda_events)])
    
    mappings = []
    processed = 0
    
    # Process one symptom at a time
    vaers_list = list(vaers_symptoms.keys())
    
    for i, symptom in enumerate(vaers_list):
        
        print(f"Processing symptom {i+1}/{len(vaers_list)}: {symptom}")
        
        prompt = f"""Map this VAERS symptom to FDA adverse events. The symptom can map to MULTIPLE FDA events if appropriate.

FDA ADVERSE EVENTS:
{fda_events_str}

VAERS SYMPTOM TO MAP:
{symptom}

Find ALL matching FDA adverse events for this symptom. Return as a list (can be empty if no matches).

Return JSON format:
{{"vaers_symptom": "{symptom}", "fda_adverse_events": ["match1", "match2"]}}

Rules:
- Look for exact matches, synonyms, and related terms
- Return ALL relevant matches, not just the best one
- Use empty list [] if no good matches exist"""

        payload = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            if 'content' not in result or not result['content']:
                print(f"  ERROR: No content in response")
                continue
                
            content = result['content'][0]['text']
            
            # Parse JSON response
            try:
                # Extract JSON object from response
                start_pos = content.find('{')
                end_pos = content.rfind('}') + 1
                
                if start_pos == -1 or end_pos == 0:
                    print(f"  No JSON object found in response")
                    continue
                
                json_content = content[start_pos:end_pos]
                
                mapping = json.loads(json_content)
                mappings.append(mapping)
                processed += 1
                fda_matches = mapping.get('fda_adverse_events', [])
                print(f"  ✓ Mapped to {len(fda_matches)} FDA events: {fda_matches}")
                
                # Save progress every 10 mappings
                if processed % 10 == 0:
                    with open('../json_data/symptom_mappings.json', 'w') as f:
                        json.dump(mappings, f, indent=2)
                    print(f"  💾 Saved progress: {processed}/{len(vaers_list)} completed")
                
            except json.JSONDecodeError as e:
                print(f"  JSON parsing error: {e}")
                print(f"  Skipping this symptom...")
                continue
                    
        except Exception as e:
            print(f"  API error: {e}")
            print(f"  Skipping this symptom...")
            continue
        
        # Rate limiting
        time.sleep(0.5)
    
    # Final save
    with open('../json_data/symptom_mappings.json', 'w') as f:
        json.dump(mappings, f, indent=2)
    print(f"🎉 Final save: {len(mappings)} mappings completed")
    
    return mappings

def main():
    """Create symptom mappings using Claude"""
    print("Creating symptom mappings with Claude...")
    
    # Get data
    vaers_symptoms = get_vaers_symptoms()
    fda_events = get_fda_adverse_events()
    
    # Create mappings
    mappings = map_symptoms_with_claude(vaers_symptoms, fda_events)
    
    # Save mappings
    with open('../json_data/symptom_mappings.json', 'w') as f:
        json.dump(mappings, f, indent=2)
    
    # Print summary
    total_mappings = len(mappings)
    with_matches = sum(1 for m in mappings if len(m.get('fda_adverse_events', [])) > 0)
    
    print(f"\nCompleted symptom mappings!")
    print(f"Total VAERS symptoms processed: {total_mappings}")
    print(f"Symptoms with FDA matches: {with_matches}")
    if total_mappings > 0:
        print(f"Match rate: {with_matches/total_mappings*100:.1f}%")
    else:
        print("Match rate: N/A (no mappings created)")

if __name__ == "__main__":
    main()