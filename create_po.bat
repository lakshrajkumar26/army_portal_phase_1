@echo off
echo ========================================
echo    CREATE PO USER - 2 STC Portal
echo ========================================
echo.

set /p username="Enter PO Username: "
set /p password="Enter PO Password: "
set /p email="Enter Email (optional, press Enter to skip): "
set /p firstname="Enter First Name (optional, press Enter to skip): "
set /p lastname="Enter Last Name (optional, press Enter to skip): "

echo.
echo Creating PO user...
echo.

if "%email%"=="" (
    if "%firstname%"=="" (
        python manage.py create_po_user --username=%username% --password=%password%
    ) else (
        python manage.py create_po_user --username=%username% --password=%password% --first-name="%firstname%" --last-name="%lastname%"
    )
) else (
    python manage.py create_po_user --username=%username% --password=%password% --email=%email% --first-name="%firstname%" --last-name="%lastname%"
)

echo.
echo ========================================
pause
