#!/usr/bin/env python3
"""
Verify the comprehensive test data
"""

import pandas as pd

def verify_data():
    df = pd.read_csv('comprehensive_test_questions.csv')
    
    print('📊 Data Verification:')
    print(f'Total questions: {len(df)}')
    print()
    
    # Check distribution by trade
    print('🏢 Trade Distribution:')
    trade_counts = df['trade'].value_counts()
    for trade, count in trade_counts.items():
        print(f'   {trade}: {count} questions')
    print()
    
    # Check distribution by paper type
    print('📄 Paper Type Distribution:')
    paper_counts = df['paper_type'].value_counts()
    for paper, count in paper_counts.items():
        print(f'   {paper}: {count} questions')
    print()
    
    # Check distribution by question set
    print('📦 Question Set Distribution:')
    set_counts = df['question_set'].value_counts().sort_index()
    for set_name, count in set_counts.items():
        print(f'   Set {set_name}: {count} questions')
    print()
    
    # Check part distribution for DMV PRIMARY Set A
    dmv_primary_a = df[(df['trade'] == 'DMV') & (df['paper_type'] == 'PRIMARY') & (df['question_set'] == 'A')]
    print('📝 DMV PRIMARY Set A Part Distribution:')
    part_counts = dmv_primary_a['part'].value_counts().sort_index()
    for part, count in part_counts.items():
        print(f'   Part {part}: {count} questions')
    print()
    
    # Verify against HARD_CODED_TRADE_CONFIG
    expected_dmv = {"A": 20, "C": 5, "D": 15, "E": 4, "F": 10}
    print('✅ Verification against HARD_CODED_TRADE_CONFIG:')
    for part, expected_count in expected_dmv.items():
        actual_count = part_counts.get(part, 0)
        status = "✅" if actual_count == expected_count else "❌"
        print(f'   Part {part}: Expected {expected_count}, Got {actual_count} {status}')
    
    print()
    print('📋 Sample Questions:')
    
    # Part A (MCQ)
    part_a = df[df['part'] == 'A'].iloc[0]
    print('Part A (MCQ):')
    print(f'   Q: {part_a["question"][:80]}...')
    print(f'   Correct: {part_a["correct_answer"]}')
    print()
    
    # Part C (Short Answer)
    part_c = df[df['part'] == 'C'].iloc[0]
    print('Part C (Short Answer):')
    print(f'   Q: {part_c["question"]}')
    print()
    
    # Part F (True/False)
    part_f = df[df['part'] == 'F'].iloc[0]
    print('Part F (True/False):')
    print(f'   Q: {part_f["question"]}')
    print(f'   Options: {part_f["option_a"]}, {part_f["option_b"]}')
    print(f'   Correct: {part_f["correct_answer"]}')
    print()
    
    # Show different sets
    print('🎯 Different Sets Sample:')
    for set_name in ['A', 'B', 'C']:
        set_sample = df[(df['trade'] == 'DMV') & (df['paper_type'] == 'PRIMARY') & 
                       (df['question_set'] == set_name) & (df['part'] == 'A')].iloc[0]
        print(f'   Set {set_name}: {set_sample["question"][:60]}...')

if __name__ == "__main__":
    verify_data()