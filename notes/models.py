from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Note(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    faculty = models.CharField(max_length=50)
    subject = models.CharField(max_length=50)
    title = models.CharField(max_length=100, default="Title")
    upload_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='all_notes/', blank=True, null=True)

    def __str__(self):
        return self.subject

