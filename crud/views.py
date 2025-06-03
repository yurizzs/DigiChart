from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import User, Patient, VitalSigns
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.db.models.functions import TruncDate
from datetime import date
from django.contrib.auth.decorators import login_required, user_passes_test

# Create your views here.

def get_current_user(request):
    if request.user.is_authenticated:
        try:
            return User.objects.get(username=request.user.username)
        except User.DoesNotExist:
            return None

def add_user(request):
    try:
        base_data = {
            'gender_choices': User.GENDER_CHOICES,
            'role_choices': User.ROLE_CHOICES,
        }   
        
        if request.method == 'POST':
            full_name = request.POST.get('full_name')
            gender = request.POST.get('gender')
            role = request.POST.get('role')
            birth_date = request.POST.get('birth_date')
            address = request.POST.get('address')
            contact_number = request.POST.get('contact_number')
            username = request.POST.get('username')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
                
            if password !=confirm_password:
                messages.error(request, "Password and Confirm Password do not match.")
                data = {
                    'full_name': full_name,
                    'gender': gender,
                    'role': role,
                    'birth_date': birth_date,
                    'address': address,
                    'contact_number': contact_number,
                    'username': username
                }
                data.update(base_data)
                return render(request, 'user/AddUser.html', data)
            
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                data = {
                    'full_name': full_name,
                    'gender': gender,
                    'role': role,
                    'birth_date': birth_date,
                    'address': address,
                    'contact_number': contact_number,
                    'username': username
                }
                data.update(base_data)
                return render(request, 'user/AddUser.html', data)
            
            User.objects.create(
                full_name=full_name,
                gender=gender,
                role=role,
                birth_date=birth_date,
                address=address,
                contact_number=contact_number,
                username=username,
                password=make_password(password)    
            ).save()
            messages.success(request, "User added successfully.")
            return redirect('/user/list')      
        
        return render(request, 'user/AddUser.html', base_data)
    
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}") 

def user_list(request):
    try:
        search_query = request.GET.get('search', '')
        user_list = User.objects.all()
        
        if search_query:
            user_list = user_list.filter(
                full_name__icontains=search_query
            ) | user_list.filter(
                username__icontains=search_query
            ) | user_list.filter(
                role__icontains=search_query
            )
        
        return render(request, 'user/UserList.html', {'users': user_list})
    except Exception as e:
        return HttpResponse(f'Error alert: {e}')
    
def edit_user(request, user_id):
    try:
        userObj = User.objects.get(pk=user_id)
        
        if request.method == 'POST':    
            full_name = request.POST.get('full_name')
            gender = request.POST.get('gender')
            role = request.POST.get('role')
            birth_date = request.POST.get('birth_date')
            address = request.POST.get('address')
            contact_number = request.POST.get('contact_number')
            username = request.POST.get('username')
            
            if User.objects.filter(username=username).exclude(user_id=user_id).exists():
                messages.error(request, 'Username already exists. Please choose a different username.')
                return redirect(f'/user/edit/{user_id}')
            
            userObj.full_name = full_name
            userObj.gender = gender
            userObj.role = role
            userObj.birth_date = birth_date
            userObj.address = address
            userObj.contact_number = contact_number
            userObj.username = username
            userObj.save()
            
            messages.success(request, 'User updated successfully.')
            return redirect('/user/list')
        
        return render(request, 'user/EditUser.html', {
            'user': userObj,
            'gender_choices': User.GENDER_CHOICES,
            'role_choices': User.ROLE_CHOICES,
        })
    except Exception as e:
        return HttpResponse(f'Error ulit:{e}')

def delete_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        if request.method == 'POST':
            user.delete()
            messages.success(request, f'User {user.username} has been deleted successfully.')
            return redirect('/user/list')
        else:
            return render (request, 'user/DeleteUser.html', {'user': user})
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('/user/list')
    except Exception as e:
        return HttpResponse(f'Error ulit: {e}')
   
def add_patient(request):
    try:
        base_data = {
            'gender_choices': User.GENDER_CHOICES,
            'status_choices': Patient.STATUS_CHOICES,
            'blood_types': Patient.BLOOD_TYPES,
            'physicians': User.objects.filter(role='D'),
            'nurses': User.objects.filter(role='N'),
        }
        if request.method == 'POST':
            first_name = request.POST.get('first_name')
            middle_name = request.POST.get('middle_name')
            last_name = request.POST.get('last_name')
            gender = request.POST.get('gender')
            age = request.POST.get('age')
            birth_date = request.POST.get('birth_date')
            height = request.POST.get('height')
            weight = request.POST.get('weight')
            lmp = request.POST.get('lmp') or None
            address = request.POST.get('address')
            contact_number = request.POST.get('contact_number')
            temperature_on_admission = request.POST.get('temperature_on_admission')
            pulse_on_admission = request.POST.get('pulse_on_admission')
            respiration_on_admission = request.POST.get('respiration_on_admission')
            blood_pressure_on_admission = request.POST.get('blood_pressure_on_admission')
            o_sat_on_admission = request.POST.get('o_sat_on_admission')
            status = request.POST.get('status')
            religion = request.POST.get('religion')
            blood_type = request.POST.get('blood_type')
            admission_date = request.POST.get('admission_date')
            physician_id = request.POST.get('physician')
            nurse_id = request.POST.get('nurse')
            chief_complaint = request.POST.get('chief_complaint')
            admitting_diagnosis = request.POST.get('admitting_diagnosis')
            past_illness = request.POST.get('past_illness')
            previous_hospitalization = request.POST.get('previous_hospitalization')
            surgeries = request.POST.get('surgeries')
            injuries = request.POST.get('injuries')
            family_history = request.POST.get('family_history')
            
            nurse = User.objects.get(user_id=nurse_id) if nurse_id else None
            physician = User.objects.get(user_id=physician_id) if physician_id else None
            
            Patient.objects.create(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                gender=gender,
                age=age,
                birth_date=birth_date,
                height=height,
                weight=weight,
                lmp=lmp,
                address=address,
                contact_number=contact_number, 
                temperature_on_admission=temperature_on_admission,
                pulse_on_admission=pulse_on_admission,
                respiration_on_admission=respiration_on_admission,
                blood_pressure_on_admission=blood_pressure_on_admission,
                o_sat_on_admission=o_sat_on_admission,
                status=status,
                religion=religion,
                blood_type=blood_type,
                admission_date=admission_date,
                physician=physician,
                nurse=nurse,
                chief_complaint=chief_complaint,
                admitting_diagnosis=admitting_diagnosis,
                past_illness=past_illness,
                previous_hospitalization=previous_hospitalization,
                surgeries=surgeries,
                injuries=injuries,
                family_history=family_history
            ).save()  
            messages.success(request, "Patient added successfully.") 
            return redirect('/patient/list')
    
        return render(request, 'nurse/AddPatient.html', base_data)
            
    except Exception as e:
        return HttpResponse(f'Error sa tabi tabi: {e}')
    
def patient_list(request):
    try:
        search_query = request.GET.get('search', '')
        patient_list = Patient.objects.all()
        
        if search_query:
            patient_list = patient_list.filter(
                first_name__icontains=search_query
            ) | patient_list.filter(
                middle_name__icontains=search_query
            ) | patient_list.filter(
                last_name__icontains=search_query
            ) | patient_list.filter(
                physician__full_name__icontains=search_query
            ) | patient_list.filter(
                blood_type__icontains=search_query
            )
            
        return render(request, 'nurse/PatientList.html', {
            'patients': patient_list,
            'search_query': search_query
        })
    except Exception as e:
        return HttpResponse(f'Error lang dyan: {e}')
    
def edit_patient(request, patient_id):
    try:
        patientObj = Patient.objects.get(pk=patient_id)
        
        if request.method == 'POST':
            first_name = request.POST.get('first_name')
            middle_name = request.POST.get('middle_name')
            last_name = request.POST.get('last_name')
            gender = request.POST.get('gender')
            age = request.POST.get('age')
            birth_date = request.POST.get('birth_date')
            height = request.POST.get('height')
            weight = request.POST.get('weight')
            lmp = request.POST.get('lmp') or None
            address = request.POST.get('address')
            contact_number = request.POST.get('contact_number')
            temperature_on_admission = request.POST.get('temperature_on_admission')
            pulse_on_admission = request.POST.get('pulse_on_admission')
            respiration_on_admission = request.POST.get('respiration_on_admission')
            blood_pressure_on_admission = request.POST.get('blood_pressure_on_admission')
            o_sat_on_admission = request.POST.get('o_sat_on_admission')
            status = request.POST.get('status')
            religion = request.POST.get('religion')
            blood_type = request.POST.get('blood_type')
            admission_date = request.POST.get('admission_date')
            physician_id = request.POST.get('physician')
            nurse_id = request.POST.get('nurse')
            chief_complaint = request.POST.get('chief_complaint')
            admitting_diagnosis = request.POST.get('admitting_diagnosis')
            past_illness = request.POST.get('past_illness')
            previous_hospitalization = request.POST.get('previous_hospitalization')
            surgeries = request.POST.get('surgeries')
            injuries = request.POST.get('injuries')
            family_history = request.POST.get('family_history')
            
            nurse = User.objects.get(user_id=nurse_id) if nurse_id else None
            physician = User.objects.get(user_id=physician_id) if physician_id else None
            
            patientObj.first_name = first_name
            patientObj.middle_name = middle_name
            patientObj.last_name = last_name
            patientObj.gender = gender
            patientObj.age = age
            patientObj.birth_date = birth_date
            patientObj.height = height
            patientObj.weight = weight
            patientObj.lmp = lmp
            patientObj.address = address
            patientObj.contact_number = contact_number
            patientObj.temperature_on_admission = temperature_on_admission
            patientObj.pulse_on_admission = pulse_on_admission
            patientObj.respiration_on_admission = respiration_on_admission
            patientObj.blood_pressure_on_admission = blood_pressure_on_admission
            patientObj.o_sat_on_admission = o_sat_on_admission
            patientObj.status = status
            patientObj.religion = religion
            patientObj.blood_type = blood_type
            patientObj.admission_date = admission_date
            patientObj.physician = physician
            patientObj.nurse = nurse
            patientObj.chief_complaint = chief_complaint
            patientObj.admitting_diagnosis = admitting_diagnosis
            patientObj.past_illness = past_illness
            patientObj.previous_hospitalization = previous_hospitalization
            patientObj.surgeries = surgeries
            patientObj.injuries = injuries
            patientObj.family_history = family_history
            patientObj.save()
            
            messages.success(request, 'Patiend updated successfully.')
            return redirect('/patient/list')
        
        return render(request, 'nurse/EditPatient.html', {
            'patient': patientObj,
            'gender_choices': Patient.GENDER_CHOICES,
            'status_choices': Patient.STATUS_CHOICES,
            'blood_types': Patient.BLOOD_TYPES,
            'physicians': User.objects.filter(role='D'),
            'nurses': User.objects.filter(role='N'),
        })
    except Exception as e:
        return HttpResponse(f'Error:{e}')

def show_information(request, patient_id):
    try:
        patient = Patient.objects.get(pk=patient_id)
        return render(request, 'nurse/ShowInformation.html', {'patient': patient})
    except Exception as e:
        return HttpResponse(f'Error: {e}')
    
def add_vitals(request):
    try:
        if request.method == 'POST':
            patient_id = request.POST.get('patient_id')  # get patient_id from form
            patient = get_object_or_404(Patient, pk=patient_id)

            temperature = request.POST.get('temperature')
            pulse = request.POST.get('pulse')
            respiration = request.POST.get('respiration')
            blood_pressure = request.POST.get('blood_pressure')
            o_sat = request.POST.get('o_sat')
            time = request.POST.get('time')
            date = request.POST.get('date')

            # Save the new vital sign record linked to the patient
            VitalSigns.objects.create(
                patient=patient,
                temperature=temperature,
                pulse=pulse,
                respiration=respiration,
                blood_pressure=blood_pressure,
                o_sat=o_sat,
                time=time,
                date=date
            )

            messages.success(request, 'Vital signs added successfully.')
            return redirect(f'/vitals/info/{patient_id}')  # Redirect as needed

        # For GET request, show the form and pass all patients
        patients = Patient.objects.all()
        return render(request, 'nurse/VitalSign.html', {'patients': patients})

    except Exception as e:
        return HttpResponse(f'Error da ah: {e}')

def patient_vitals(request, patient_id):
    try:
        patient = get_object_or_404(Patient, pk=patient_id)
        vitals = VitalSigns.objects.filter(patient_id=patient_id).order_by('-date', '-time')

        return render(request, 'nurse/PatientVitals.html', {
            'patient': patient,
            'vitals': vitals
        })
    except Exception as e:
        return HttpResponse(f'Error fetching vitals: {e}')

def nurse_dashboard(request):
    try:
        today = date.today()
        
        total_patients_today = Patient.objects.annotate(
            admission_day=TruncDate('admission_date')
        ).filter(admission_day=today).count()
        vitals_today = VitalSigns.objects.filter(date=today).count()
        
        data = {
            'total_patients_today': total_patients_today,
            'vitals_today': vitals_today,
            'pending_task': 3,
        }
        
        return render(request, 'dashboard/NurseDashboard.html', data)
    except Exception as e:
        return HttpResponse(f'Errowr: {e}')
    
def admin_dashboard(request):
    today = date.today()

    total_patients = Patient.objects.count()
    admissions_today = Patient.objects.filter(admission_date__date=today).count()

    total_physicians = User.objects.filter(role='D').count()  # 'D' for Doctor
    total_nurses = User.objects.filter(role='N').count()      # 'N' for Nurse

    context = {
        'total_patients': total_patients,
        'admissions_today': admissions_today,
        'total_physicians': total_physicians,
        'total_nurses': total_nurses,
    }

    return render(request, 'dashboard/AdminDash.html', context)