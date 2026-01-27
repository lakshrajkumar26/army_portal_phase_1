from django.db import models

# This app doesn't need actual models - it's just for admin interface organization
# We'll create a simple model that doesn't interact with the database

class ExamDataCleanup(models.Model):
    """Model for organizing data management in admin - no database interaction"""
    
    # Add a dummy field to make Django happy, but we'll override all admin methods
    id = models.AutoField(primary_key=True)
    
    class Meta:
        managed = False  # Don't create database table
        verbose_name = "Data Management System"
        verbose_name_plural = "Data Management System"
        
    def __str__(self):
        return "Data Management System"