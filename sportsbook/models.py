from django.db import models
from django.utils import timezone
from core.models import Match

class BoostWindow(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='boosts')
    multiplier = models.DecimalField(max_digits=4, decimal_places=2, help_text="e.g. 1.25 for +25% odds")
    start_time = models.DateTimeField()
    end_time   = models.DateTimeField()

    def is_active(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def __str__(self):
        return f"{self.match} ×{self.multiplier} ({self.start_time}–{self.end_time})"
