# questions/csv_processor.py
import csv
from io import StringIO
from django.core.exceptions import ValidationError
from .models import Question, Trade


class QuestionCSVProcessor:
    """Enhanced CSV processor for the new question upload format"""
    
    REQUIRED_COLUMNS = [
        'question', 'part', 'marks', 'option_a', 'option_b', 
        'option_c', 'option_d', 'correct_answer', 'trade', 
        'paper_type', 'question_set', 'is_common', 'is_active'
    ]
    
    VALID_PARTS = ['A', 'B', 'C', 'D', 'E', 'F']
    VALID_PAPER_TYPES = ['PRIMARY', 'SECONDARY']
    VALID_QUESTION_SETS = [chr(i) for i in range(ord('A'), ord('Z')+1)]
    VALID_CORRECT_ANSWERS = ['option_a', 'option_b', 'option_c', 'option_d']
    
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.errors = []
        self.warnings = []
        self.processed_count = 0
        
    def validate_and_process(self):
        """Main processing method with comprehensive validation"""
        try:
            # Reset file pointer
            self.csv_file.seek(0)
            
            # Read and validate CSV structure
            content = self.csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(StringIO(content))
            
            # Validate headers
            if not self._validate_headers(csv_reader.fieldnames):
                return False, []
                
            # Process each row
            questions_to_create = []
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header
                question_data = self._validate_row(row, row_num)
                if question_data:
                    questions_to_create.append(question_data)
            
            # Return data for bulk creation by caller
            if not self.errors:
                self.processed_count = len(questions_to_create)
                return True, questions_to_create
                
            return False, []
            
        except Exception as e:
            self.errors.append(f"File processing error: {str(e)}")
            return False, []
    
    def bulk_create_questions(self, questions_data):
        """Bulk create questions from validated data"""
        if questions_data:
            Question.objects.bulk_create([
                Question(**data) for data in questions_data
            ])
            return len(questions_data)
        return 0
    
    def _validate_headers(self, headers):
        """Validate CSV headers match required format"""
        if not headers:
            self.errors.append("CSV file appears to be empty or invalid")
            return False
            
        missing_columns = set(self.REQUIRED_COLUMNS) - set(headers)
        if missing_columns:
            self.errors.append(f"Missing required columns: {', '.join(missing_columns)}")
            return False
            
        # Check for old JSON format
        if 'options' in headers:
            self.errors.append(
                "Old JSON format detected. Please use separate option_a, option_b, "
                "option_c, option_d columns instead of 'options' column."
            )
            return False
            
        return True
    
    def _validate_row(self, row, row_num):
        """Validate individual row and return question data"""
        row_errors = []
        
        # Validate required fields are not empty
        for field in self.REQUIRED_COLUMNS:
            if not row.get(field, '').strip():
                row_errors.append(f"Column '{field}' is empty")
        
        if row_errors:
            self.errors.append(f"Row {row_num}: {'; '.join(row_errors)}")
            return None
            
        # Validate specific field values
        if row['part'] not in self.VALID_PARTS:
            row_errors.append(f"Invalid part '{row['part']}'. Must be one of: {', '.join(self.VALID_PARTS)}")
            
        if row['paper_type'] not in self.VALID_PAPER_TYPES:
            row_errors.append(f"Invalid paper_type '{row['paper_type']}'. Must be PRIMARY or SECONDARY")
            
        if row['question_set'] not in self.VALID_QUESTION_SETS:
            row_errors.append(f"Invalid question_set '{row['question_set']}'. Must be A-Z")
            
        if row['correct_answer'] not in self.VALID_CORRECT_ANSWERS:
            row_errors.append(f"Invalid correct_answer '{row['correct_answer']}'. Must be option_a, option_b, option_c, or option_d")
        
        # Validate marks is numeric
        try:
            marks = float(row['marks'])
            if marks <= 0:
                row_errors.append("Marks must be greater than 0")
        except ValueError:
            row_errors.append(f"Invalid marks value '{row['marks']}'. Must be a number")
            
        # Validate boolean fields
        is_common = row['is_common'].lower() in ['true', '1', 'yes']
        is_active = row['is_active'].lower() in ['true', '1', 'yes']
        
        # Validate trade exists
        try:
            trade = Trade.objects.get(code=row['trade'])
        except Trade.DoesNotExist:
            row_errors.append(f"Trade '{row['trade']}' does not exist")
            trade = None
            
        if row_errors:
            self.errors.append(f"Row {row_num}: {'; '.join(row_errors)}")
            return None
            
        return {
            'text': row['question'].strip(),
            'part': row['part'],
            'marks': marks,
            'option_a': row['option_a'].strip(),
            'option_b': row['option_b'].strip(),
            'option_c': row['option_c'].strip(),
            'option_d': row['option_d'].strip(),
            'correct_answer': [row['correct_answer']],  # Keep as JSON for compatibility
            'trade': trade,
            'paper_type': row['paper_type'],
            'question_set': row['question_set'],
            'is_common': is_common,
            'is_active': is_active,
        }