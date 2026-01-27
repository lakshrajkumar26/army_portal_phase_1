#!/usr/bin/env python3
"""
Script to convert the sample CSV to Excel format for testing the new upload system.
"""

import pandas as pd
import sys
import os

def create_excel_from_csv():
    """Convert CSV to Excel format"""
    try:
        # Read the CSV file
        df = pd.read_csv('sample_questions_comprehensive.csv')
        
        # Create Excel file
        excel_filename = 'sample_questions_new_format.xlsx'
        df.to_excel(excel_filename, index=False, engine='openpyxl')
        
        print(f"✅ Successfully created {excel_filename}")
        print(f"📊 Total questions: {len(df)}")
        print(f"📋 Columns: {', '.join(df.columns.tolist())}")
        
        # Show sample data
        print("\n📝 Sample data (first 3 rows):")
        print(df.head(3).to_string())
        
        # Show question set distribution
        print(f"\n🎯 Question Set Distribution:")
        set_dist = df['question_set'].value_counts().sort_index()
        for set_name, count in set_dist.items():
            print(f"   Set {set_name}: {count} questions")
        
        # Show trade distribution
        print(f"\n🏢 Trade Distribution:")
        trade_dist = df['trade'].value_counts()
        for trade, count in trade_dist.items():
            print(f"   {trade}: {count} questions")
            
        print(f"\n📁 File created: {os.path.abspath(excel_filename)}")
        print("\n🔧 Instructions:")
        print("1. You can now convert this Excel file to .dat format using your converter")
        print("2. Upload the .dat file through the admin interface")
        print("3. The system will detect the new CSV format and process accordingly")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating Excel file: {str(e)}")
        return False

if __name__ == "__main__":
    create_excel_from_csv()