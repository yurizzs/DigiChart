from django.db import models

# Create your models here.

class User(models.Model):
    class Meta:
        db_table = 'tbl_users'
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female')
    ]
    
    ROLE_CHOICES = [
        ('N', 'Nurse'),
        ('D', 'Doctor')
    ]
    
    user_id = models.BigAutoField(primary_key=True, blank=False)
    full_name = models.CharField(max_length=55, blank=False)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    role = models.CharField(max_length=1, choices=ROLE_CHOICES)
    birth_date = models.DateField(blank=False)
    address = models.CharField(max_length=255, blank=False)
    contact_number = models.CharField(max_length=20, blank=False)
    username = models.CharField(max_length=55, blank=False, unique=True)
    password = models.CharField(max_length=255, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Patient(models.Model):
    class Meta:
        db_table = 'tbl_patients'
    
    BLOOD_TYPES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-')
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female')
    ]
    
    STATUS_CHOICES = [
        ('S', 'Single'),
        ('M', 'Married'),
        ('D', 'Divorced'),
        ('W', 'Widowed')
    ]
    
    patient_id = models.BigAutoField(primary_key=True, blank=False)
    first_name = models.CharField(max_length=55, blank=False)
    middle_name = models.CharField(max_length=55, blank=True)
    last_name = models.CharField(max_length=55, blank=False)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField(blank=False)
    birth_date = models.DateField(blank=False)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=False)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=False)
    lmp = models.DateField(blank=True)
    address = models.CharField(max_length=255, blank=False)
    contact_number = models.CharField(max_length=20, blank=False)
    temperature = models.DecimalField(max_digits=4, decimal_places=2, blank=False)
    pulse = models.PositiveIntegerField(blank=False)
    respiration = models.PositiveIntegerField(blank=False)
    blood_pressure = models.CharField(max_length=10, blank=False)
    o_sat = models.CharField(max_length=4, blank=False)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    religion = models.CharField(max_length=55, blank=False)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES)
    admission_date = models.DateTimeField(blank=False)
    physician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False, related_name='patients_as_physician')
    nurse = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False, related_name='patiends_as_nurse')
    chief_complaint = models.TextField(blank=False)
    admitting_diagnosis = models.TextField(blank=False)
    past_illness = models.TextField(blank=False)
    previous_hospitalization = models.TextField(blank=False)
    surgeries = models.TextField(blank=False)
    injuries = models.TextField(blank=False)
    family_history = models.TextField(blank=False)
    
    @property
    def full_name(self):
        name = [self.first_name]
        if self.middle_name:
            name.append(self.middle_name)
        name.append(self.last_name)
        return ' '.join(name)