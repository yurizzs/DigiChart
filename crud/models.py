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
        ('A', 'Admin'),
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
    temperature_on_admission = models.DecimalField(max_digits=4, decimal_places=2)
    pulse_on_admission = models.PositiveIntegerField()
    respiration_on_admission = models.PositiveIntegerField()
    blood_pressure_on_admission = models.CharField(max_length=10)
    o_sat_on_admission = models.CharField(max_length=4)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def full_name(self):
        name = [self.first_name]
        if self.middle_name:
            name.append(self.middle_name)
        name.append(self.last_name)
        return ' '.join(name)
    
class VitalSigns(models.Model):
    class Meta:
        db_table = 'tbl_VitalSigns'
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vitals')
    temperature = models.DecimalField(max_digits=4, decimal_places=2)
    pulse = models.PositiveIntegerField()
    respiration = models.PositiveIntegerField()
    blood_pressure = models.CharField(max_length=10)
    o_sat = models.CharField(max_length=4)
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

def custom_login_view(request, role, template_name):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"DEBUG: Login attempt - Username: {username}, Role: {role}")

        try:
            # Find the user directly
            user = User.objects.get(username=username)
            print(f"DEBUG: User found: {user.username}")
            
            # Check password
            if check_password(password, user.password):
                print(f"DEBUG: Password correct")
                # Check role
                if user.role.upper() == role.upper():
                    print(f"DEBUG: Role matches")
                    # Set session data
                    request.session['username'] = user.username
                    request.session['role'] = user.role
                    request.session['is_authenticated'] = True
                    request.session['user_id'] = user.user_id  # or user.pk
                    
                    # Redirect based on role
                    if role.upper() == 'A':
                        return redirect('/admin/dashboard/')
                    elif role.upper() == 'D':
                        return redirect('/doctor/dashboard/')
                    elif role.upper() == 'N':
                        return redirect('/nurse/dashboard/')
                else:
                    print(f"DEBUG: Role mismatch - User role: {user.role}, Expected: {role}")
                    messages.error(request, "You are not authorized for this role.")
            else:
                print(f"DEBUG: Password incorrect")
                messages.error(request, "Invalid username or password.")
        except User.DoesNotExist:
            print(f"DEBUG: User not found")
            messages.error(request, "Invalid username or password.")

    return render(request, template_name, {'role': role, 'hide_chatbot': True})

def logout_view(request):
    # Clear all session data
    request.session.flush()
    return redirect('/login/')

def get_user_data(request):
    if request.session.get('is_authenticated'):
        try:
            user = User.objects.get(username=request.session['username'])
            return {'current_user': user}
        except User.DoesNotExist:
            return {'current_user': None}
    return {'current_user': None}