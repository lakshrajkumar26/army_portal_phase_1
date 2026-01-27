from django.db import models

# This app doesn't need actual models - it's just for admin interface organization
# We'll create proxy models to organize the cleanup functions

class ExamDataCleanup(models.Model):
    """Proxy model for organizing exam data cleanup in admin"""
    
    class Meta:
        managed = False  # Don't create database table
        verbose_name = "Clean Exam Data"
        verbose_name_plural = "Clean Exam Data"


class CompleteCleanup(models.Model):
    """Proxy model for organizing complete cleanup in admin"""
    
    class Meta:
        managed = False  # Don't create database table
        verbose_name = "Clean Everything"
        verbose_name_plural = "Clean Everything"


class ExamSlotCleanup(models.Model):
    """Proxy model for organizing exam slot cleanup in admin"""
    
    class Meta:
        managed = False  # Don't create database table
        verbose_name = "Clean Exam Slots"
        verbose_name_plural = "Clean Exam Slots"