from django.db import models

# Create your models here.
class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    department = models.CharField(max_length=100)
    salary = models.IntegerField()
    image = models.ImageField(
        upload_to='employee_images/', 
        null=True, 
        blank=True
    )

    def __str__(self):
        return self.name
