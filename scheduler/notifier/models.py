from django.db import models

class Consultant(models.Model):
    netlink = models.CharField(primary_key=True, max_length = 30)
    email = models.EmailField()
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)

class Shift(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length = 20)
    time_and_location = models.CharField(max_length = 40) # shift desc. as it appears in Homer ex. '18:30 - 23:30 (Working at CLE lab)'
    consultant = models.ForeignKey(Consultant, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('time_and_location', 'consultant',)
        ordering = ('date', 'start_time')
