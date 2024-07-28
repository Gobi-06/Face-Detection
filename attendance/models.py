from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=255)
    emp_id = models.CharField(max_length=20, unique=True)
    phone_no = models.CharField(max_length=15)
    image = models.ImageField(upload_to='employees/')

    def __str__(self):
        return self.name
