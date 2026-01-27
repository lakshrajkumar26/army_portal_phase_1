@echo off
echo ========================================
echo    EXAM ADMINISTRATION TOOL
echo ========================================
echo.

:menu
echo Please choose an option:
echo.
echo 1. Show current data statistics
echo 2. Show help for all commands
echo 3. Reset exam sessions only (students can retake)
echo 4. Delete all questions and papers
echo 5. Delete all exam data (keep users)
echo 6. Complete reset (everything except superusers)
echo 7. Import new questions from Excel
echo 8. Setup trade activations
echo 9. Manage exam slots
echo 10. Exit
echo.
set /p choice="Enter your choice (1-10): "

if "%choice%"=="1" goto stats
if "%choice%"=="2" goto help
if "%choice%"=="3" goto reset_sessions
if "%choice%"=="4" goto delete_questions
if "%choice%"=="5" goto delete_exam_data
if "%choice%"=="6" goto complete_reset
if "%choice%"=="7" goto import_questions
if "%choice%"=="8" goto setup_activations
if "%choice%"=="9" goto manage_slots
if "%choice%"=="10" goto exit

echo Invalid choice. Please try again.
goto menu

:stats
echo.
echo ========================================
echo    CURRENT DATA STATISTICS
echo ========================================
python manage.py show_data_stats --detailed
echo.
pause
goto menu

:help
echo.
echo ========================================
echo    ADMINISTRATION HELP
echo ========================================
python manage.py exam_admin_help
echo.
pause
goto menu

:reset_sessions
echo.
echo ========================================
echo    RESET EXAM SESSIONS
echo ========================================
echo This will delete exam sessions and results but keep questions and users.
echo Students will be able to retake exams.
echo.
python manage.py reset_exam_sessions --dry-run
echo.
set /p confirm="Do you want to proceed? (y/n): "
if /i "%confirm%"=="y" (
    python manage.py reset_exam_sessions --confirm
    echo.
    echo ✅ Exam sessions reset successfully!
) else (
    echo Operation cancelled.
)
echo.
pause
goto menu

:delete_questions
echo.
echo ========================================
echo    DELETE QUESTIONS AND PAPERS
echo ========================================
echo This will delete all questions, papers, and uploads but keep users and exam sessions.
echo.
python manage.py cleanup_exam_data --level=questions --dry-run
echo.
set /p confirm="Do you want to proceed? (y/n): "
if /i "%confirm%"=="y" (
    python manage.py cleanup_exam_data --level=questions --confirm
    echo.
    echo ✅ Questions deleted successfully!
) else (
    echo Operation cancelled.
)
echo.
pause
goto menu

:delete_exam_data
echo.
echo ========================================
echo    DELETE ALL EXAM DATA
echo ========================================
echo This will delete all exam-related data but preserve user registrations.
echo.
python manage.py cleanup_exam_data --level=exam-data --dry-run
echo.
set /p confirm="Do you want to proceed? (y/n): "
if /i "%confirm%"=="y" (
    python manage.py cleanup_exam_data --level=exam-data --confirm
    echo.
    echo ✅ Exam data deleted successfully!
) else (
    echo Operation cancelled.
)
echo.
pause
goto menu

:complete_reset
echo.
echo ========================================
echo    COMPLETE SYSTEM RESET
echo ========================================
echo ⚠️  WARNING: This will delete EVERYTHING except superuser accounts!
echo.
python manage.py cleanup_exam_data --level=everything --dry-run
echo.
set /p confirm="Are you ABSOLUTELY SURE you want to proceed? (yes/no): "
if /i "%confirm%"=="yes" (
    python manage.py cleanup_exam_data --level=everything --confirm
    echo.
    echo ✅ Complete reset done!
) else (
    echo Operation cancelled.
)
echo.
pause
goto menu

:import_questions
echo.
echo ========================================
echo    IMPORT QUESTIONS FROM EXCEL
echo ========================================
echo Available Excel files:
dir *.xlsx /b 2>nul
echo.
set /p filename="Enter Excel filename (with .xlsx extension): "
if exist "%filename%" (
    python manage.py import_questions "%filename%"
    echo.
    echo ✅ Questions imported successfully!
) else (
    echo File not found: %filename%
)
echo.
pause
goto menu

:setup_activations
echo.
echo ========================================
echo    SETUP TRADE ACTIVATIONS
echo ========================================
python manage.py setup_trade_activations
echo.
echo ✅ Trade activations setup complete!
pause
goto menu

:manage_slots
echo.
echo ========================================
echo    EXAM SLOT MANAGEMENT
echo ========================================
echo.
echo 1. Show slot status for all candidates
echo 2. Assign slots to all candidates
echo 3. Reset all slots
echo 4. Reassign all slots
echo 5. Manage slots by trade
echo 6. Delete all candidates
echo 7. Back to main menu
echo.
set /p slot_choice="Enter your choice (1-7): "

if "%slot_choice%"=="1" goto slot_status
if "%slot_choice%"=="2" goto assign_all_slots
if "%slot_choice%"=="3" goto reset_all_slots
if "%slot_choice%"=="4" goto reassign_all_slots
if "%slot_choice%"=="5" goto manage_by_trade
if "%slot_choice%"=="6" goto delete_all_candidates
if "%slot_choice%"=="7" goto menu

echo Invalid choice. Please try again.
goto manage_slots

:slot_status
echo.
echo ========================================
echo    SLOT STATUS REPORT
echo ========================================
python manage.py manage_exam_slots status
echo.
pause
goto manage_slots

:assign_all_slots
echo.
echo ========================================
echo    ASSIGN SLOTS TO ALL CANDIDATES
echo ========================================
echo This will assign exam slots to candidates who don't have them.
echo.
python manage.py manage_exam_slots assign --dry-run
echo.
set /p confirm="Do you want to proceed? (y/n): "
if /i "%confirm%"=="y" (
    python manage.py manage_exam_slots assign
    echo.
    echo ✅ Slots assigned successfully!
) else (
    echo Operation cancelled.
)
echo.
pause
goto manage_slots

:reset_all_slots
echo.
echo ========================================
echo    RESET ALL SLOTS
echo ========================================
echo ⚠️  WARNING: This will reset ALL exam slots!
echo.
python manage.py manage_exam_slots reset --dry-run
echo.
set /p confirm="Are you sure you want to proceed? (y/n): "
if /i "%confirm%"=="y" (
    python manage.py manage_exam_slots reset
    echo.
    echo ✅ All slots reset successfully!
) else (
    echo Operation cancelled.
)
echo.
pause
goto manage_slots

:reassign_all_slots
echo.
echo ========================================
echo    REASSIGN ALL SLOTS
echo ========================================
echo This will reset and reassign exam slots for ALL candidates.
echo.
python manage.py manage_exam_slots reassign --dry-run
echo.
set /p confirm="Do you want to proceed? (y/n): "
if /i "%confirm%"=="y" (
    python manage.py manage_exam_slots reassign
    echo.
    echo ✅ All slots reassigned successfully!
) else (
    echo Operation cancelled.
)
echo.
pause
goto manage_slots

:manage_by_trade
echo.
echo ========================================
echo    MANAGE SLOTS BY TRADE
echo ========================================
echo.
set /p trade_name="Enter trade name (e.g., OCC, DMV, TTC): "
if "%trade_name%"=="" goto manage_slots

echo.
echo 1. Show status for %trade_name%
echo 2. Assign slots for %trade_name%
echo 3. Reset slots for %trade_name%
echo 4. Back to slot menu
echo.
set /p trade_choice="Enter your choice (1-4): "

if "%trade_choice%"=="1" goto trade_status
if "%trade_choice%"=="2" goto trade_assign
if "%trade_choice%"=="3" goto trade_reset
if "%trade_choice%"=="4" goto manage_slots

echo Invalid choice.
goto manage_by_trade

:trade_status
echo.
echo Status for trade: %trade_name%
python manage.py manage_exam_slots status --trade "%trade_name%"
echo.
pause
goto manage_by_trade

:trade_assign
echo.
echo Assigning slots for trade: %trade_name%
python manage.py manage_exam_slots assign --trade "%trade_name%" --dry-run
echo.
set /p confirm="Proceed with assignment? (y/n): "
if /i "%confirm%"=="y" (
    python manage.py manage_exam_slots assign --trade "%trade_name%"
    echo ✅ Slots assigned for %trade_name%!
) else (
    echo Operation cancelled.
)
echo.
pause
goto manage_by_trade

:trade_reset
echo.
echo Resetting slots for trade: %trade_name%
python manage.py manage_exam_slots reset --trade "%trade_name%" --dry-run
echo.
set /p confirm="Proceed with reset? (y/n): "
if /i "%confirm%"=="y" (
    python manage.py manage_exam_slots reset --trade "%trade_name%"
    echo ✅ Slots reset for %trade_name%!
) else (
    echo Operation cancelled.
)
echo.
pause
goto manage_by_trade

:delete_all_candidates
echo.
echo ========================================
echo    DELETE ALL CANDIDATES
echo ========================================
echo ⚠️  WARNING: This will delete ALL candidate registrations and profiles!
echo.
echo This will delete:
echo - All candidate profiles and user accounts
echo - All candidate answers and exam sessions
echo - All candidate photos and data
echo.
echo This will preserve:
echo - Questions and question papers
echo - Admin accounts
echo - Exam configuration
echo.
python manage.py cleanup_exam_data --level=candidates --dry-run
echo.
set /p confirm="Are you ABSOLUTELY SURE you want to delete all candidates? (yes/no): "
if /i "%confirm%"=="yes" (
    python manage.py cleanup_exam_data --level=candidates --confirm
    echo.
    echo ✅ All candidates deleted successfully!
) else (
    echo Operation cancelled.
)
echo.
pause
goto manage_slots

:exit
echo.
echo Thank you for using the Exam Administration Tool!
pause
exit