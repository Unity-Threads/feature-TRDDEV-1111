from django.db import models

class AboutUs(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)

    story = models.TextField()
    mission = models.TextField()
    unique_points = models.TextField()
    quality = models.TextField()
    founders_note = models.TextField()
    contact_email = models.EmailField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About Us Content"
        verbose_name_plural = "About Us Content"

    def __str__(self):
        return self.title


# --------------------------------------------------
# NEW MODEL (make sure this is OUTSIDE the AboutUs class)
# --------------------------------------------------
class TimelineEvent(models.Model):
    year = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.year} - {self.title}"
