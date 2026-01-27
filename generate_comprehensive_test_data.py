#!/usr/bin/env python3
"""
Generate comprehensive test data for DMV and OCC trades with proper question distribution.
DMV: 54 questions × 2 paper types × 5 sets = 540 questions
OCC: 54 questions × 2 paper types × 5 sets = 540 questions
Total: 1,080 questions
"""

import csv
import pandas as pd

# Configuration from HARD_CODED_TRADE_CONFIG
TRADE_CONFIG = {
    "DMV": {"total_questions": 54, "part_distribution": {"A": 20, "B": 0, "C": 5, "D": 15, "E": 4, "F": 10}},
    "OCC": {"total_questions": 54, "part_distribution": {"A": 20, "B": 0, "C": 5, "D": 15, "E": 4, "F": 10}},
}

PAPER_TYPES = ["PRIMARY", "SECONDARY"]
QUESTION_SETS = ["A", "B", "C", "D", "E"]

def generate_question_text(trade, paper_type, part, question_num, set_name):
    """Generate unique question text based on parameters"""
    if part == "A":  # MCQ
        return f"{trade} {paper_type} Set {set_name} Part A MCQ Question {question_num}: What is the correct procedure for {trade.lower()} operation {question_num}?"
    elif part == "C":  # Short answer
        return f"{trade} {paper_type} Set {set_name} Part C: Explain {trade.lower()} concept {question_num} briefly (20-30 words)."
    elif part == "D":  # Fill in blanks
        return f"{trade} {paper_type} Set {set_name} Part D: Fill in the blank - {trade.lower()} procedure {question_num} requires _______ steps."
    elif part == "E":  # Long answer
        return f"{trade} {paper_type} Set {set_name} Part E: Describe {trade.lower()} operational procedure {question_num} in detail (100-120 words)."
    elif part == "F":  # True/False
        return f"{trade} {paper_type} Set {set_name} Part F: {trade.lower()} safety protocol {question_num} is mandatory for all operations."
    else:
        return f"{trade} {paper_type} Set {set_name} Part {part} Question {question_num}"

def generate_options(trade, part, question_num, set_name):
    """Generate options based on question type"""
    if part == "A":  # MCQ
        base_options = [
            f"{trade} Option A for Q{question_num}",
            f"{trade} Option B for Q{question_num}",
            f"{trade} Option C for Q{question_num}",
            f"{trade} Option D for Q{question_num}"
        ]
        # Vary correct answer based on set and question number
        correct_idx = (ord(set_name) - ord('A') + question_num) % 4
        return base_options, f"option_{chr(ord('a') + correct_idx)}"
    elif part == "F":  # True/False
        # Alternate True/False based on question number
        correct = "True" if question_num % 2 == 1 else "False"
        return ["True", "False", "", ""], "option_a" if correct == "True" else "option_b"
    else:  # C, D, E (no options needed)
        return ["", "", "", ""], "option_a"

def generate_comprehensive_data():
    """Generate all questions for DMV and OCC"""
    questions = []
    
    for trade in TRADE_CONFIG.keys():
        config = TRADE_CONFIG[trade]
        part_dist = config["part_distribution"]
        
        for paper_type in PAPER_TYPES:
            for set_name in QUESTION_SETS:
                question_counter = 1
                
                # Generate questions for each part
                for part, count in part_dist.items():
                    if count == 0:  # Skip parts with 0 questions
                        continue
                        
                    for i in range(count):
                        options, correct_answer = generate_options(trade, part, question_counter, set_name)
                        
                        question_text = generate_question_text(trade, paper_type, part, question_counter, set_name)
                        
                        # Determine marks based on part
                        marks = {
                            "A": 1,  # MCQ
                            "C": 2,  # Short answer
                            "D": 1,  # Fill in blanks
                            "E": 5,  # Long answer
                            "F": 1   # True/False
                        }.get(part, 1)
                        
                        question_data = {
                            "question": question_text,
                            "part": part,
                            "marks": marks,
                            "option_a": options[0],
                            "option_b": options[1],
                            "option_c": options[2],
                            "option_d": options[3],
                            "correct_answer": correct_answer,
                            "trade": trade,
                            "paper_type": paper_type,
                            "question_set": set_name,
                            "is_common": "FALSE",
                            "is_active": "TRUE"
                        }
                        
                        questions.append(question_data)
                        question_counter += 1
    
    return questions

def create_csv_file():
    """Create the comprehensive CSV file"""
    print("🚀 Generating comprehensive test data...")
    
    questions = generate_comprehensive_data()
    
    # Write to CSV
    filename = "comprehensive_test_questions.csv"
    fieldnames = [
        "question", "part", "marks", "option_a", "option_b", "option_c", "option_d",
        "correct_answer", "trade", "paper_type", "question_set", "is_common", "is_active"
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(questions)
    
    print(f"✅ Created {filename}")
    print(f"📊 Total questions generated: {len(questions)}")
    
    # Show breakdown
    print("\n📋 Question Breakdown:")
    
    for trade in TRADE_CONFIG.keys():
        trade_questions = [q for q in questions if q['trade'] == trade]
        print(f"\n🏢 {trade}: {len(trade_questions)} questions")
        
        for paper_type in PAPER_TYPES:
            paper_questions = [q for q in trade_questions if q['paper_type'] == paper_type]
            print(f"   📄 {paper_type}: {len(paper_questions)} questions")
            
            for set_name in QUESTION_SETS:
                set_questions = [q for q in paper_questions if q['question_set'] == set_name]
                print(f"      📦 Set {set_name}: {len(set_questions)} questions")
                
                # Show part distribution for first set as sample
                if set_name == "A":
                    part_counts = {}
                    for q in set_questions:
                        part = q['part']
                        part_counts[part] = part_counts.get(part, 0) + 1
                    
                    part_str = ", ".join([f"{part}:{count}" for part, count in sorted(part_counts.items())])
                    print(f"         📝 Parts: {part_str}")
    
    return filename

def create_excel_file(csv_filename):
    """Convert CSV to Excel"""
    try:
        df = pd.read_csv(csv_filename)
        excel_filename = csv_filename.replace('.csv', '.xlsx')
        df.to_excel(excel_filename, index=False, engine='openpyxl')
        
        print(f"✅ Created Excel file: {excel_filename}")
        print(f"📁 File size: {len(df)} rows")
        
        return excel_filename
    except Exception as e:
        print(f"❌ Error creating Excel file: {e}")
        return None

if __name__ == "__main__":
    csv_file = create_csv_file()
    excel_file = create_excel_file(csv_file)
    
    print(f"\n🎯 Test Data Summary:")
    print(f"   • DMV: 54 × 2 × 5 = 540 questions")
    print(f"   • OCC: 54 × 2 × 5 = 540 questions")
    print(f"   • Total: 1,080 questions")
    print(f"\n📁 Files created:")
    print(f"   • CSV: {csv_file}")
    if excel_file:
        print(f"   • Excel: {excel_file}")
    
    print(f"\n🔧 Next steps:")
    print(f"   1. Convert Excel to .dat using your converter")
    print(f"   2. Upload through admin interface")
    print(f"   3. Test question set activation")
    print(f"   4. Test global PRIMARY/SECONDARY controls")