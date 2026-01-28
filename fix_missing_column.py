#!/usr/bin/env python3
"""
Fix script to manually add the missing slot_attempting_at column
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def check_and_add_column():
    """Check if the column exists and add it if missing"""
    
    with connection.cursor() as cursor:
        # Check if the column exists
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'registration_candidateprofile' 
            AND COLUMN_NAME = 'slot_attempting_at'
        """)
        
        result = cursor.fetchone()
        
        if result:
            print("✅ Column 'slot_attempting_at' already exists in the database")
            return True
        else:
            print("❌ Column 'slot_attempting_at' is missing from the database")
            print("🔧 Adding the missing column...")
            
            try:
                # Add the missing column
                cursor.execute("""
                    ALTER TABLE registration_candidateprofile 
                    ADD COLUMN slot_attempting_at datetime(6) NULL
                """)
                print("✅ Successfully added 'slot_attempting_at' column")
                return True
            except Exception as e:
                print(f"❌ Failed to add column: {str(e)}")
                return False

def verify_table_structure():
    """Verify the complete table structure"""
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'registration_candidateprofile' 
            AND COLUMN_NAME LIKE '%slot%'
            ORDER BY COLUMN_NAME
        """)
        
        columns = cursor.fetchall()
        
        print("\n📋 Current slot-related columns in registration_candidateprofile:")
        for column in columns:
            print(f"   - {column[0]} ({column[1]}, nullable: {column[2]})")
        
        expected_columns = [
            'has_exam_slot',
            'slot_assigned_at', 
            'slot_assigned_by_id',
            'slot_attempting_at',
            'slot_consumed_at'
        ]
        
        existing_columns = [col[0] for col in columns]
        missing_columns = [col for col in expected_columns if col not in existing_columns]
        
        if missing_columns:
            print(f"\n❌ Missing columns: {missing_columns}")
            return False
        else:
            print("\n✅ All expected slot columns are present")
            return True

if __name__ == "__main__":
    print("🔍 Checking database structure for slot_attempting_at column...")
    
    try:
        # First verify the current structure
        structure_ok = verify_table_structure()
        
        if not structure_ok:
            # Try to add the missing column
            column_added = check_and_add_column()
            
            if column_added:
                # Verify again after adding
                print("\n🔍 Verifying structure after adding column...")
                verify_table_structure()
            else:
                print("\n❌ Failed to fix the database structure")
                sys.exit(1)
        
        print("\n🎉 Database structure is correct!")
        
    except Exception as e:
        print(f"\n❌ Error checking database: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)