from django.db import models

# Create your models here.
class Links(models.Model):
    uid = models.AutoField(primary_key=True)
    user = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    url = models.URLField(verbose_name = "URL", help_text="Enter URL to start crawling")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'title', 'url']

    def __str__(self):
        display_name = self.url
        if self.title is not None:
            display_name = self.title
        return display_name

class User(models.Model):
    uid = models.AutoField(primary_key=True)

    def __str__(self):
        return str(self.uid)
