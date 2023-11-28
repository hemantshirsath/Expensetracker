from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.models import User
class Goal(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    amount_to_save = models.DecimalField(max_digits=10, decimal_places=2)
    current_saved_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    

    def calculate_progress(self):
        total_days = (self.end_date - self.start_date).days
        saved_percentage = (self.current_saved_amount / self.amount_to_save) * 100
        days_remaining = (self.end_date - timezone.now().date()).days

        # Check if there are days remaining to avoid division by zero
        if days_remaining > 0:
            daily_savings_required = (self.amount_to_save - self.current_saved_amount) / days_remaining
        else:
            daily_savings_required = 0  # or handle the situation in an appropriate way

        return {
            "saved_percentage": round(saved_percentage, 2),
            "daily_savings_required": round(daily_savings_required, 2),
        }
