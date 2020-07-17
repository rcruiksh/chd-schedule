from django.db import models

class Consultant(models.Model):
    netlink = models.CharField(primary_key=True, max_length = 30)
    email = models.EmailField()
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)


class Shift(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    day = models.IntegerField()
    start_hour = models.IntegerField()
    start_min = models.IntegerField()
    end_hour = models.IntegerField()
    end_min = models.IntegerField()
    location = models.CharField(max_length = 20)
    time_and_location = models.CharField(max_length = 40) # shift desc. as it appears in Homer ex. '18:30 - 23:30 (Working at CLE lab)'
    consultant = models.ForeignKey(Consultant, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('time_and_location', 'consultant',)

    def __str__(self):
        return '{}-{}-{}: {}'.format(self.year, self.month, self.day, self.time_and_location)

    def comparisonDict(self):
        return {"year": self.year, "month": self.month, "day": self.day, "start_hour": self.start_hour, "start_min": self.start_min, "end_hour": self.end_hour, "end_min": self.end_min, "location": self.location, "time_and_location": self.time_and_location, "consultant": self.consultant.netlink}

class PastShift(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    day = models.IntegerField()
    start_hour = models.IntegerField()
    start_min = models.IntegerField()
    end_hour = models.IntegerField()
    end_min = models.IntegerField()
    location = models.CharField(max_length = 20)
    time_and_location = models.CharField(max_length = 40) # shift desc. as it appears in Homer ex. '18:30 - 23:30 (Working at CLE lab)'
    consultant = models.ForeignKey(Consultant, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('time_and_location', 'consultant',)

    def __str__(self):
        return '{}-{}-{}: {}'.format(self.year, self.month, self.day, self.time_and_location)

    def comparisonDict(self):
        return {"year": self.year, "month": self.month, "day": self.day, "start_hour": self.start_hour, "start_min": self.start_min, "end_hour": self.end_hour, "end_min": self.end_min, "location": self.location, "time_and_location": self.time_and_location, "consultant": self.consultant.netlink}
