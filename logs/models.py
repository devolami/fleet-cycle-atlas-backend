from django.db import models

class LogbookTrip(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    total_distance_miles = models.FloatField()
    total_driving_time_mins = models.FloatField()
    pickup_time_mins = models.FloatField()
    current_cycle_hour = models.FloatField(default=0.0)
    
    def __str__(self):
        return f"Trip {self.id} - {self.total_distance_miles} miles"