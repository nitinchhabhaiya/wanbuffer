from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator

# Create your models here.
gender_choices = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
)

mobile_validation = RegexValidator(regex=r'^\+?1?\d{9,15}$',message="Enter Mobile No!")

class UserDetails(models.Model):
    fullname = models.CharField(max_length=150,default="")
    mobile_no = models.CharField(max_length=10, validators=[mobile_validation,MinLengthValidator(10)],unique=True)
    email = models.EmailField(max_length=150,blank=True,null=True,default="")
    # dob = models.DateField(auto_now=False,blank=True,null=True)
    gender = models.CharField(max_length=10,default="",choices=gender_choices)
    # address = models.TextField(default="",null=True,blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'userdetails'
        ordering = ('-created_date',)
        
    def __str__(self):
        return self.fullname