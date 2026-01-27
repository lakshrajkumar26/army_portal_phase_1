# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Roles(models.TextChoices):
        OIC_ADMIN = "OIC_ADMIN", "OIC Admin"  # Officer In Charge
        CANDIDATE = "CANDIDATE", "Candidate"
        PO_ADMIN = "PO_ADMIN", "PO Admin"  # Presiding Officer

    role = models.CharField(
        max_length=32, choices=Roles.choices, default=Roles.CANDIDATE, db_index=True
    )

    # optional link to a center (set later; FK declared here to avoid circular imports at runtime)
    center = models.ForeignKey(
        "centers.Center",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    def str(self):
        return f"{self.username} ({self.role})"