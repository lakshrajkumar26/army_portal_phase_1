from django.db import models

COMD_CHOICES = [
    ("SC", "Southern Command"),
    ("EC", "Eastern Command"),
    ("WC", "Western Command"),
    ("CC", "Central Command"),
    ("NC", "Northern Command"),
    ("SWC", "South Western Command"),
    ("ANC", "Andaman & Nicobar Command"),
    ("ARTRAC", "ARTRAC"),
]

EXAM_CENTER_CHOICES = {
    "SC": [
        ("Secunderabad", "Secunderabad"),
        ("Jhansi", "Jhansi"),
        ("Ahmedabad", "Ahmedabad"),
        ("Jodhpur", "Jodhpur"),
        ("Saugor", "Saugor"),
        ("Bhopal", "Bhopal"),
        ("Pune", "Pune"),
    ],
    "EC": [
        ("Binnaguri", "Binnaguri"),
        ("Kolkata", "Kolkata"),
        ("Missamari", "Missamari"),
        ("Rangapahar", "Rangapahar"),
        ("Dinjan", "Dinjan"),
        ("Gangtok", "Gangtok"),
        ("Leimakhong", "Leimakhong"),
        ("Tenga", "Tenga"),
        ("Panagarh", "Panagarh"),
        ("Ranchi", "Ranchi"),
        ("Likabali", "Likabali"),
        ("Tejpur", "Tejpur"),
        ("Kalimpong", "Kalimpong"),
    ],
    "WC": [
        ("Jalandhar", "Jalandhar"),
        ("Ambala", "Ambala"),
        ("Delhi", "Delhi"),
        ("Amritsar", "Amritsar"),
        ("Ferozepur", "Ferozepur"),
        ("Patiala", "Patiala"),
        ("Jammu", "Jammu"),
        ("Pathankot", "Pathankot"),
        ("Chandimandir", "Chandimandir"),
    ],
    "CC": [
        ("Meerut", "Meerut"),
        ("Agra", "Agra"),
        ("Bareilly", "Bareilly"),
        ("Jabalpur", "Jabalpur"),
        ("Lucknow", "Lucknow"),
        ("Ranikhet", "Ranikhet"),
        ("Dehradun", "Dehradun"),
        ("Udhampur", "Udhampur"),
        ("Baramulla", "Baramulla"),
        ("Kargil", "Kargil"),
        ("Leh", "Leh"),
    ],
    "NC": [
        ("Srinagar", "Srinagar"),
        ("Kupwara", "Kupwara"),
        ("Allahabad", "Allahabad"),
        ("Rajouri", "Rajouri"),
        ("Akhnoor", "Akhnoor"),
        ("Nagrota", "Nagrota"),
        ("Pathankot", "Pathankot"),
        ("Mathura", "Mathura"),
        ("Keru", "Keru"),
    ],
    "SWC": [
        ("Jaipur", "Jaipur"),
        ("Hissar", "Hissar"),
        ("Bathinda", "Bathinda"),
        ("Sriganganagar", "Sriganganagar"),
        ("Bikaner", "Bikaner"),
        ("Suratgarh", "Suratgarh"),
        ("Kota", "Kota"),
    ],
    "ANC": [
        ("Port Blair", "Port Blair"),
    ],
    "ARTRAC": [
        ("Ahmednagar", "Ahmednagar"),
        ("Bangalore", "Bangalore"),
        ("Chennai", "Chennai"),
        ("Pune MINTSD", "Pune MINTSD"),
        ("MCTE Mhow", "MCTE Mhow"),
    ],
}


class Center(models.Model):
    comd = models.CharField(max_length=20, choices=COMD_CHOICES, blank=True)
    exam_Center = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Exam center"
        verbose_name_plural = "Exam centers"

    def __str__(self):
        return f"{self.comd} - {self.exam_Center}"