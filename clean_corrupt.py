
import os

def clean_corrupt_files(file_list):
    cleaned_count = 0
    error_count = 0
    
    for filepath in file_list:
        try:
            # Read as binary
            with open(filepath, 'rb') as f:
                content = f.read()
            
            if b'\x00' in content:
                print(f"Cleaning {filepath}...")
                # Remove null bytes
                clean_content = content.replace(b'\x00', b'')
                
                # Write back
                with open(filepath, 'wb') as f:
                    f.write(clean_content)
                cleaned_count += 1
            else:
                print(f"No null bytes found in {filepath}")
                
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            error_count += 1
            
    print(f"\nSummary: Cleaned {cleaned_count} files. Errors: {error_count}")

files_to_clean = [
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\add_march_schedules.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\check_payment_intent.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\check_student_work.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\fix_booking_121.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\populate_data.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\test_paymongo_setup.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\test_pricing.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\verify_payment_security.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\app\admin.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\app\models.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\fbs_instructor\urls.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\fbs_instructor\views.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\flightapp\views.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\flightapp\management\commands\update_ml_prices.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\flightapp\ml\dynamic_pricing.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\flightapp\ml\predictor.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\flightapp\ml\test_model.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\flightapp\ml\validate_predictions.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\flightapp\services\email_service.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\flightapp\services\grading_service.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\flightapp\services\paymongo_service.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\flightapp\services\pdf_service.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\scripts\seed_seats.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\scripts\test_pricing.py",
    r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend\scripts\verify_grading.py"
]

if __name__ == "__main__":
    clean_corrupt_files(files_to_clean)
