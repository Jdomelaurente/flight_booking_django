import os
import django
import random

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import Students, UserProfile
from fbs_instructor.models import Section, SectionEnrollment
from django.db import transaction

def insert_students():
    section_code = 'ABCD'
    password = 'FFll24()'
    count = 25
    
    try:
        section = Section.objects.get(section_code=section_code)
        print(f"Found section: {section.section_name} ({section.section_code})")
    except Section.DoesNotExist:
        print(f"Error: Section with code {section_code} not found.")
        return

    first_names = ["Juan", "Maria", "Jose", "Ana", "Luis", "Elena", "Pedro", "Rosa", "Antonio", "Teresa", 
                   "Miguel", "Isabel", "Francisco", "Carmen", "Rafael", "Lucia", "Diego", "Beatriz", "Carlos", "Julia",
                   "Manuel", "Sofia", "Alejandro", "Victoria", "Fernando"]
    last_names = ["Santos", "Reyes", "Cruz", "Bautista", "Ocampo", "Garcia", "Mendoza", "Pascual", "Castillo", "Villanueva",
                  "Ramos", "Castro", "Rivera", "Aquino", "Corpuz", "Solano", "Torres", "Lim", "Go", "Tan",
                  "Sy", "Uy", "Chua", "Perez", "Tolentino"]

    with transaction.atomic():
        for i in range(1, count + 1):
            student_index = f"{i:02d}"
            username = f"std_bstm2a_{student_index}"
            student_number = f"STU-BSTM2A-{student_index}"
            
            # Create User
            if User.objects.filter(username=username).exists():
                print(f"User {username} already exists, skipping...")
                continue
                
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f"{username}@example.com"
            
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            # Update UserProfile role to student (signal created it with None)
            profile = UserProfile.objects.get(user=user)
            profile.role = 'student'
            profile.save()
            
            # Create Student record
            student_record = Students.objects.create(
                user=user,
                student_number=student_number,
                first_name=first_name,
                last_name=last_name,
                email=email,
                course='BSTM',
                year_level='2'
            )
            
            # Enroll in Section
            SectionEnrollment.objects.get_or_create(
                section=section,
                student=student_record
            )
            
            print(f"Created and enrolled: {username} ({student_number})")

    print(f"Successfully inserted and enrolled {count} students.")

if __name__ == "__main__":
    insert_students()
