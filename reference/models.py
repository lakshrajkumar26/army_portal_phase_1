# reference/models.py
from django.db import models

# class Trade(models.Model):
#     name = models.CharField(max_length=120, unique=True)
#     code = models.CharField(max_length=30, unique=True)

#     def __str__(self): return f"{self.code} - {self.name}"



class Trade(models.Model):
    """
    14 categories total (we'll seed later).
    """
    name = models.CharField(max_length=80, unique=True)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self): return f"{self.code}"
    
    class Meta:
        verbose_name = "Trade"
        verbose_name_plural = "Trades"


