from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import User, Patient, VitalSigns
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.db.models.functions import TruncDate
from datetime import date, timedelta
from django.db.models import Count
import re
from django.http import JsonResponse

# Create your views here.

def custom_login_view(request, role, template_name):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"DEBUG: Login attempt - Username: {username}, Role: {role}")

        try:
            # Find the user directly
            user = User.objects.get(username=username)
            print(f"DEBUG: User found: {user.username}")
            
            # Check password using check_password
            if check_password(password, user.password):
                print(f"DEBUG: Password correct")
                # Check role
                if user.role.upper() == role.upper():
                    print(f"DEBUG: Role matches")
                    # Set session data
                    request.session['username'] = user.username
                    request.session['role'] = user.role
                    request.session['is_authenticated'] = True
                    
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


def home_page(request):
    try:
        return render(request, 'login/login.html', {'hide_chatbot': True})
    except Exception as e:
        return HttpResponse(f'Error: {e}')
    
def nurse_login(request):
    try:
        return custom_login_view(request, 'N', 'login/nurse_login.html')
    except Exception as e:
        return HttpResponse(f'Error: {e}')
    
def admin_login(request):
    try:
        return custom_login_view(request, 'A', 'login/admin_login.html')
    except Exception as e:
        return HttpResponse(f'Error: {e}')
    
def doctor_login(request):
    try:
        return custom_login_view(request, 'D', 'login/doctor_login.html')
    except Exception as e:
        return HttpResponse(f'Error: {e}')

def logout_view(request):
    request.session.flush()
    return redirect('/home/')

def get_current_user(request):
    if request.session.get('is_authenticated'):
        try:
            return User.objects.get(username=request.session['username'])
        except User.DoesNotExist:
            return None
    return None

def add_user(request):
    try:
        current_user = get_current_user(request)
        base_data = {
            'gender_choices': User.GENDER_CHOICES,
            'role_choices': User.ROLE_CHOICES,
            'current_user': current_user,
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
            return redirect('/user/list/')      
        
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
        
        paginator = Paginator(user_list, 5)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        current_user = get_current_user(request)
        
        return render(request, 'user/UserList.html', {
            'users': page_obj,  # Changed from user_list to page_obj
            'current_user': current_user,
            'page_obj': page_obj,
            'search_query': search_query
        })
    except Exception as e:
        return HttpResponse(f'Error alert: {e}')
    
def edit_user(request, user_id):
    try:
        userObj = User.objects.get(pk=user_id)
        current_user = get_current_user(request)
        
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
            'current_user': current_user
        })
    except Exception as e:
        return HttpResponse(f'Error ulit:{e}')

def delete_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        current_user = get_current_user(request)
        if request.method == 'POST':
            user.delete()
            messages.success(request, f'User {user.username} has been deleted successfully.')
            return redirect('/user/list')
        else:
            return render (request, 'user/DeleteUser.html', {'user': user, 'current_user': current_user})
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('/user/list')
    except Exception as e:
        return HttpResponse(f'Error ulit: {e}')
    
def changepass(request, user_id):
    try:
        if request.method == 'POST':
            user = User.objects.get(pk=user_id)
            current_user = get_current_user(request)
            current_password = request.POST.get('current_password')
            password = request.POST.get('password')
            confirmPassword = request.POST.get('confirm_password')
            
            if not check_password(current_password, user.password):
                messages.error(request, 'Current password is incorrect.')
                return redirect(f'/user/changepass/{user_id}')
            
            if not password and not confirmPassword:
                messages.error(request, 'Please fill out both fields')
                return redirect(f'/user/changepass/{user_id}')
            
            if password != confirmPassword:
                messages.error(request, 'New password and confirm password doesn`t match')
                return redirect(f'/user/changepass/{user_id}')
            
            user.password = make_password(password)
            user.save()
            messages.success(request, 'Password successfully change!')
            return redirect('/user/list')
        else:
            user = User.objects.get(pk=user_id)
            return render(request, 'user/ChangePass.html', {'user': user, 'current_user': current_user})
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('/user/list')
    except Exception as e:
        return HttpResponse(f'Error: {e}')
   
def add_patient(request):
    try:
        current_user = get_current_user(request)
        base_data = {
            'gender_choices': User.GENDER_CHOICES,
            'status_choices': Patient.STATUS_CHOICES,
            'blood_types': Patient.BLOOD_TYPES,
            'physicians': User.objects.filter(role='D'),
            'nurses': User.objects.filter(role='N'),
            'current_user': current_user,
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
        current_user = get_current_user(request)
        
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
            
        paginator = Paginator(patient_list, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'nurse/PatientList.html', {
            'patients': patient_list,
            'search_query': search_query,
            'current_user': current_user,
            'page_obj': page_obj,
        })
    except Exception as e:
        return HttpResponse(f'Error lang dyan: {e}')
    
def edit_patient(request, patient_id):
    try:
        patientObj = Patient.objects.get(pk=patient_id)
        current_user = get_current_user(request)
        
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
            'current_user': current_user
        })
    except Exception as e:
        return HttpResponse(f'Error:{e}')

def show_information(request, patient_id):
    try:
        patient = Patient.objects.get(pk=patient_id)
        # return render(request, 'nurse/ShowInformation.html', {'patient': patient})
        vitals = VitalSigns.objects.filter(patient_id=patient_id).order_by('-date', '-time')
        current_user = get_current_user(request)

        return render(request, 'nurse/ShowInformation.html', {
            'patient': patient,
            'vitals': vitals,
            'current_user': current_user,
        })
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
        current_user = get_current_user(request)
        return render(request, 'nurse/VitalSign.html', {'patients': patients, 'current_user': current_user})

    except Exception as e:
        return HttpResponse(f'Error da ah: {e}')

def patient_vitals(request, patient_id):
    try:
        patient = get_object_or_404(Patient, pk=patient_id)
        current_user = get_current_user(request)

        # Get unique vital sign dates
        date_qs = (
            VitalSigns.objects
            .filter(patient_id=patient_id)
            .annotate(day=TruncDate('date'))
            .values_list('day', flat=True)
            .distinct()
            .order_by('-day')
        )

        selected_date_str = request.GET.get('selected_date')
        selected_date = None
        page_obj = None

        if selected_date_str:
            try:
                selected_date = date.fromisoformat(selected_date_str)
            except ValueError:
                selected_date = None
        else:
            paginator = Paginator(date_qs, 1)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            selected_date = page_obj.object_list[0] if page_obj.object_list else None

        # Filter vitals by selected date
        vitals = VitalSigns.objects.filter(
            patient_id=patient_id,
            date=selected_date
        ).order_by('-date', '-time')
        
        # Get vitals for selected date (only if a date is selected)
        if selected_date:
            vitals = VitalSigns.objects.filter(
                patient_id=patient_id,
                date=selected_date
            ).order_by('-date', '-time')
        else:
            vitals = VitalSigns.objects.none()  # nothing to show

        return render(request, 'nurse/PatientVitals.html', {
            'patient': patient,
            'vitals': vitals,
            'selected_date': selected_date,
            'page_obj': page_obj,
            'date_options': date_qs,
            'current_user': current_user
        })

    except Exception as e:
        return HttpResponse(f'Error fetching vitals: {e}')
    
def nurse_dashboard(request):
    try:
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        
        total_patients_today = Patient.objects.annotate(
            admission_day=TruncDate('admission_date')
        ).filter(admission_day=today).count()
        vitals_today = VitalSigns.objects.filter(date=today).count()
        
        # Get current user data
        current_user = get_current_user(request)
        
        vitals_by_day = (
        VitalSigns.objects
        .filter(date__range=[start_of_week, today])
        .annotate(day=TruncDate('date'))
        .values('day')
        .annotate(total=Count('id'))
        .order_by('day')
    )

        # Format for chart
        vitals_chart_labels = [v['day'].strftime('%a') for v in vitals_by_day]
        vitals_chart_data = [v['total'] for v in vitals_by_day]

        data = {
            'total_patients_today': total_patients_today,
            'vitals_today': vitals_today,
            'pending_task': 3,
            'current_user': current_user,
            'vitals_chart_labels': vitals_chart_labels,
            'vitals_chart_data': vitals_chart_data,
        }
        
        return render(request, 'dashboard/NurseDashboard.html', data)
    except Exception as e:
        return HttpResponse(f'Errowr: {e}')
    
def admin_dashboard(request):
    today = date.today()

    # Dashboard counts
    total_patients = Patient.objects.count()
    admissions_today = Patient.objects.filter(admission_date__date=today).count()
    total_physicians = User.objects.filter(role='D').count()
    total_nurses = User.objects.filter(role='N').count()
    current_user = get_current_user(request)

    # Chart data for the past 7 days
    start_date = today - timedelta(days=6)
    admissions = (
        Patient.objects
        .filter(admission_date__date__gte=start_date)
        .annotate(day=TruncDate('admission_date'))
        .values('day')
        .annotate(count=Count('patient_id'))
        .order_by('day')
    )

    # Prepare labels and data
    day_map = {ad['day']: ad['count'] for ad in admissions}
    chart_labels = []
    chart_data = []

    for i in range(7):
        day = start_date + timedelta(days=i)
        chart_labels.append(day.strftime("%a"))  # e.g., Mon, Tue
        chart_data.append(day_map.get(day, 0))

    context = {
        'total_patients': total_patients,
        'admissions_today': admissions_today,
        'total_physicians': total_physicians,
        'total_nurses': total_nurses,
        'current_user': current_user,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }

    return render(request, 'dashboard/AdminDash.html', context)

def doctor_dashboard(request):
    try:
        today = date.today()
        total_patients = Patient.objects.count()
        total_physician = User.objects.filter(role='D').count()
        total_nurses = User.objects.filter(role='N').count()
        admission_today = Patient.objects.filter(admission_date__date = today).count()
        current_user = get_current_user(request)
        
        data = {
            'total_patients': total_patients,
            'total_physician': total_physician,
            'total_nurses': total_nurses,
            'admission_today': admission_today,
            'current_user': current_user
        }
        
        return render(request, 'dashboard/DoctorDash.html', data)
    except Exception as e:
        return HttpResponse(f'Error: {e}')

def chatbot_query(request):
    query = request.GET.get("q", "").strip().lower()
    print(f"Received query: {query}")  # Debug print

    # Check for BP
    match_bp = re.search(r'show last bp for (.+)', query)
    # Check for temperature
    match_temp = re.search(r'show last temperature for (.+)', query)
    match_pulse = re.search(r'show last pulse for (.+)', query)
    match_respiration = re.search(r'show last respiration for (.+)', query)
    match_o_sat = re.search(r'show last osat for (.+)', query)

    match = match_bp or match_temp or match_pulse or match_respiration or match_o_sat

    if match:
        name = match.group(1).strip().title()
        print(f"Extracted name: {name}")

        name_parts = name.split()
        if len(name_parts) < 2:
            return JsonResponse({"response": "Please provide both first and last name."})

        first_name = name_parts[0]
        last_name = name_parts[-1]

        patient = Patient.objects.filter(
            first_name__icontains=first_name,
            last_name__icontains=last_name
        ).first()

        if not patient and len(name_parts) > 2:
            middle_name = ' '.join(name_parts[1:-1])
            patient = Patient.objects.filter(
                first_name__icontains=first_name,
                middle_name__icontains=middle_name,
                last_name__icontains=last_name
            ).first()

        if not patient:
            return JsonResponse({"response": f"No patient found with name '{name}'."})

        last_vitals = patient.vitals.order_by('-date', '-time').first()

        if last_vitals:
            if match_bp:
                return JsonResponse({
                    "response": f"{patient.full_name}'s last BP was {last_vitals.blood_pressure} on {last_vitals.date.strftime('%B %d')}."
                })
            elif match_temp:
                return JsonResponse({
                    "response": f"{patient.full_name}'s last temperature was {last_vitals.temperature} on {last_vitals.date.strftime('%B %d')}."
                })
            elif match_pulse:
                return JsonResponse({
                    "response": f"{patient.full_name}'s last pulse rate was {last_vitals.pulse} on {last_vitals.date.strftime('%B %d')}."
                })
            elif match_respiration:
                return JsonResponse({
                    "response": f"{patient.full_name}'s last respiration was {last_vitals.respiration} on {last_vitals.date.strftime('%B %d')}."
                })
            elif match_o_sat:
                return JsonResponse({
                    "response": f"{patient.full_name}'s last oxygen saturation was {last_vitals.o_sat} on {last_vitals.date.strftime('%B %d')}."
                })
        else:
            return JsonResponse({"response": f"No vitals found for {patient.full_name}."})

    return JsonResponse({
        "response": "Sorry, I didn't understand that. Try: 'Show last BP for Eva Murphy' or 'Show last temperature for Eva Murphy'."
    })
