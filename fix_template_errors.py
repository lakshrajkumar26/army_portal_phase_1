#!/usr/bin/env python3
"""
Quick fix for template variable errors
Specifically addresses the VariableDoesNotExist errors
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def fix_jazzmin_settings():
    """Update Django settings to fix Jazzmin theme issues"""
    print("🔧 Fixing Jazzmin theme settings...")
    
    settings_file = Path('config/settings.py')
    
    # Check if JAZZMIN_SETTINGS exists
    with open(settings_file, 'r') as f:
        content = f.read()
    
    if 'JAZZMIN_SETTINGS' not in content:
        # Add JAZZMIN_SETTINGS to fix theme issues
        jazzmin_config = '''

# =============================================================================
# JAZZMIN ADMIN THEME CONFIGURATION
# =============================================================================

JAZZMIN_SETTINGS = {
    "site_title": "Exam Portal Admin",
    "site_header": "Military Examination Portal",
    "site_brand": "Exam Portal",
    "site_logo": None,
    "login_logo": None,
    "login_logo_dark": None,
    "site_logo_classes": "img-circle",
    "site_icon": None,
    "welcome_sign": "Welcome to Military Examination Portal",
    "copyright": "Military Examination Portal",
    "search_model": ["auth.User", "questions.Question"],
    "user_avatar": None,
    
    # Top Menu
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Support", "url": "https://github.com/", "new_window": True},
        {"model": "auth.User"},
    ],
    
    # User Menu
    "usermenu_links": [
        {"name": "Support", "url": "https://github.com/", "new_window": True},
        {"model": "auth.user"}
    ],
    
    # Side Menu
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["auth", "questions", "registration", "centers"],
    
    # Icons
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "questions": "fas fa-question-circle",
        "questions.Question": "fas fa-question",
        "registration": "fas fa-user-plus",
        "centers": "fas fa-building",
    },
    
    # UI Tweaks
    "custom_links": {
        "questions": [{
            "name": "Upload Questions", 
            "url": "admin:questions_questionupload_add", 
            "icon": "fas fa-upload",
            "permissions": ["questions.add_question"]
        }]
    },
    
    # Theme settings to fix template errors
    "theme": "cyborg",
    "dark_mode_theme": None,  # Fix for dark_mode_theme error
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    
    # Changeform settings
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    
    # Language settings
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-dark navbar-primary",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "cyborg",
    "dark_mode_theme": None,  # Fix for template error
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}
'''
        
        # Add before the security validation section
        content = content.replace(
            '# =============================================================================\n# SECURITY VALIDATION\n# =============================================================================',
            jazzmin_config + '\n# =============================================================================\n# SECURITY VALIDATION\n# ============================================================================='
        )
        
        with open(settings_file, 'w') as f:
            f.write(content)
        
        print("✅ Added JAZZMIN_SETTINGS to fix theme errors")
    else:
        print("✅ JAZZMIN_SETTINGS already exists")

def initialize_missing_data():
    """Initialize missing database records"""
    print("🔧 Initializing missing data...")
    
    from questions.models import GlobalPaperTypeControl, UniversalSetActivation, ActivateSets
    from reference.models import Trade
    
    # Initialize GlobalPaperTypeControl
    if not GlobalPaperTypeControl.objects.exists():
        GlobalPaperTypeControl.objects.create(paper_type='PRIMARY', is_active=True)
        GlobalPaperTypeControl.objects.create(paper_type='SECONDARY', is_active=False)
        print("✅ Created GlobalPaperTypeControl records")
    
    # Initialize UniversalSetActivation
    for paper_type in ['PRIMARY', 'SECONDARY']:
        UniversalSetActivation.objects.get_or_create(
            paper_type=paper_type,
            defaults={
                'universal_set_label': None,
                'universal_duration_minutes': 180,
                'is_universal_set_active': False,
                'is_universal_duration_active': False,
            }
        )
    print("✅ Initialized UniversalSetActivation records")
    
    # Initialize ActivateSets for all trades
    trades = Trade.objects.all()
    for trade in trades:
        ActivateSets.objects.get_or_create(
            trade=trade,
            defaults={
                'active_primary_set': None,
                'active_secondary_set': None,
            }
        )
    print(f"✅ Initialized ActivateSets for {trades.count()} trades")

def main():
    """Main function"""
    print("🔧 Quick Fix for Template Errors")
    print("=" * 40)
    
    try:
        # Fix Jazzmin settings
        fix_jazzmin_settings()
        
        # Initialize missing data
        initialize_missing_data()
        
        print("\n✅ Template errors fixed!")
        print("🔄 Please restart the Django server:")
        print("   python restart_clean_server.py")
        
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()