import datetime
import random
from django.utils import timezone
from .models import (
    SchoolProfile, AcademicSession, ClassLevel, Section, Subject,
    Teacher, Student, Attendance, Timetable, FeeCategory,
    FeeInvoice, FeePayment, Exam, ExamResult, Notice
)


def seed_all():
    print("Seeding SRS School ERP data...")
    
    # 1. School Profile
    profile, created = SchoolProfile.objects.get_or_create(id=1, defaults={
        'name': "SRS International Public School",
        'short_name': "SRS School ERP",
        'tagline': "Inspiring Excellence, Nurturing Leaders",
        'affiliation_number': "CBSE-AFF/2026/SRS8892",
        'school_code': "SRS-DEL-042",
        'address': "SRS Knowledge Park, Institutional Area, Sector 62, New Delhi - 110092",
        'phone': "+91 98765 43210 / 011-28901234",
        'email': "info@srsschool.edu.in",
        'website': "https://srsschool.edu.in",
        'principal_name': "Dr. Rajeshwar Sharma, Ph.D. (Ed.)",
        'currency_symbol': "₹",
        'academic_year': "2026-2027"
    })
    
    # 2. Academic Session
    session, _ = AcademicSession.objects.get_or_create(
        name="2026-2027",
        defaults={
            'start_date': datetime.date(2026, 4, 1),
            'end_date': datetime.date(2027, 3, 31),
            'is_current': True
        }
    )
    
    # 3. Class Levels
    class_specs = [
        ("Class 6", "C06", 1),
        ("Class 7", "C07", 2),
        ("Class 8", "C08", 3),
        ("Class 9", "C09", 4),
        ("Class 10", "C10", 5),
        ("Class 11 (Sci)", "C11S", 6),
        ("Class 12 (Sci)", "C12S", 7),
    ]
    classes = {}
    for name, code, order in class_specs:
        c, _ = ClassLevel.objects.get_or_create(name=name, defaults={'code': code, 'order': order})
        classes[name] = c

    # 4. Teachers
    teacher_specs = [
        ("EMP-2026-01", "Dr. Rajeshwar", "Sharma", "Male", "principal@srsschool.edu.in", "+91 98111 22334", "Principal & Director", "Administration", "Ph.D., M.Ed.", 95000),
        ("EMP-2026-02", "Sunita", "Verma", "Female", "s.verma@srsschool.edu.in", "+91 98222 33445", "PGT Mathematics", "Mathematics", "M.Sc. Maths, B.Ed.", 55000),
        ("EMP-2026-03", "Anand", "Mishra", "Male", "a.mishra@srsschool.edu.in", "+91 98333 44556", "PGT Physics", "Science", "M.Sc. Physics, B.Ed.", 52000),
        ("EMP-2026-04", "Pooja", "Chawla", "Female", "p.chawla@srsschool.edu.in", "+91 98444 55667", "TGT English & Head", "Languages", "M.A. English, B.Ed.", 48000),
        ("EMP-2026-05", "Ramesh", "Gupta", "Male", "r.gupta@srsschool.edu.in", "+91 98555 66778", "PGT Chemistry", "Science", "M.Sc. Chemistry, NET", 50000),
        ("EMP-2026-06", "Kavita", "Nair", "Female", "k.nair@srsschool.edu.in", "+91 98666 77889", "TGT Social Studies", "Humanities", "M.A. History, B.Ed.", 46000),
        ("EMP-2026-07", "Vikas", "Bansal", "Male", "v.bansal@srsschool.edu.in", "+91 98777 88990", "PGT Computer Science", "IT & Robotics", "MCA, B.Tech CS", 58000),
        ("EMP-2026-08", "Meenakshi", "Pandey", "Female", "m.pandey@srsschool.edu.in", "+91 98888 99001", "TGT Hindi & Sanskrit", "Languages", "M.A. Hindi, B.Ed.", 44000),
    ]
    teachers = {}
    for emp_id, fname, lname, gender, email, phone, desig, dept, qual, salary in teacher_specs:
        t, _ = Teacher.objects.get_or_create(
            employee_id=emp_id,
            defaults={
                'first_name': fname,
                'last_name': lname,
                'gender': gender,
                'email': email,
                'phone': phone,
                'designation': desig,
                'department': dept,
                'qualification': qual,
                'salary': salary,
                'joining_date': datetime.date(2021, 6, 15),
                'address': "Sector 50, Noida, UP"
            }
        )
        teachers[emp_id] = t

    # 5. Sections
    sections = {}
    for c_name, c_obj in classes.items():
        for s_name, room, t_key in [("A", "Room 101", "EMP-2026-02"), ("B", "Room 102", "EMP-2026-04")]:
            sec, _ = Section.objects.get_or_create(
                class_level=c_obj,
                name=s_name,
                defaults={
                    'capacity': 40,
                    'room_number': f"Block A - {c_obj.code}{s_name}",
                    'class_teacher': teachers.get(t_key)
                }
            )
            sections[f"{c_name}_{s_name}"] = sec

    # 6. Subjects
    subj_specs = [
        ("Mathematics", "MATH101"),
        ("English Core", "ENG101"),
        ("Physics", "PHY101"),
        ("Chemistry", "CHEM101"),
        ("Biology", "BIO101"),
        ("Social Science", "SST101"),
        ("Computer Science & AI", "CS101"),
        ("Hindi Literature", "HIN101"),
    ]
    subjects = {}
    for s_name, s_code in subj_specs:
        sub, _ = Subject.objects.get_or_create(code=s_code, defaults={'name': s_name})
        # Add to all classes
        for c in classes.values():
            sub.class_levels.add(c)
        subjects[s_code] = sub

    # 7. Fee Categories
    fee_cats = [
        ("Quarterly Tuition Fee", 16500.00, "Regular academic tuition fee per quarter"),
        ("Annual Development Fee", 7500.00, "Infrastructure & campus development charge"),
        ("Examination & Assessment Fee", 2500.00, "Term exams, lab material, and report cards"),
        ("School Bus / Transport Fee", 4500.00, "Quarterly safe transport facility"),
        ("Computer & Robotics Lab Fee", 3000.00, "High-tech smart lab, coding & STEM access"),
    ]
    categories = {}
    for f_name, f_amt, f_desc in fee_cats:
        fc, _ = FeeCategory.objects.get_or_create(name=f_name, defaults={'default_amount': f_amt, 'description': f_desc})
        categories[f_name] = fc

    # 8. Students
    student_data = [
        ("SRS-2026-1001", 1, "Aarav", "Sharma", "Male", "2010-04-12", "B+", "Class 10", "A", "Ramesh Sharma", "Father", "+91 98112 00001", "ramesh.sharma@gmail.com", "Senior Architect"),
        ("SRS-2026-1002", 2, "Ananya", "Verma", "Female", "2010-08-23", "O+", "Class 10", "A", "Deepak Verma", "Father", "+91 98112 00002", "deepak.v@gmail.com", "Govt Officer"),
        ("SRS-2026-1003", 3, "Rohan", "Kapoor", "Male", "2010-01-15", "A+", "Class 10", "A", "Sanjay Kapoor", "Father", "+91 98112 00003", "sanjay.k@outlook.com", "Businessman"),
        ("SRS-2026-1004", 4, "Ishita", "Patel", "Female", "2010-11-05", "AB+", "Class 10", "A", "Kiran Patel", "Mother", "+91 98112 00004", "kiran.p@gmail.com", "Chartered Accountant"),
        ("SRS-2026-1005", 5, "Kabir", "Mehta", "Male", "2010-06-30", "O+", "Class 10", "A", "Arun Mehta", "Father", "+91 98112 00005", "arun.mehta@yahoo.com", "Doctor"),
        ("SRS-2026-1006", 1, "Diya", "Choudhary", "Female", "2010-03-18", "B-", "Class 10", "B", "Manoj Choudhary", "Father", "+91 98112 00006", "m.choudhary@gmail.com", "Advocate"),
        ("SRS-2026-1007", 2, "Aditya", "Singh", "Male", "2010-09-12", "O+", "Class 10", "B", "Rajesh Singh", "Father", "+91 98112 00007", "rajesh.singh@gmail.com", "Bank Manager"),
        ("SRS-2026-1008", 3, "Sneha", "Reddy", "Female", "2010-07-25", "A+", "Class 10", "B", "Venkat Reddy", "Father", "+91 98112 00008", "v.reddy@gmail.com", "Software Engineer"),
        
        ("SRS-2026-1009", 1, "Devansh", "Saxena", "Male", "2009-02-14", "B+", "Class 11 (Sci)", "A", "Pradeep Saxena", "Father", "+91 98112 00009", "p.saxena@gmail.com", "Civil Engineer"),
        ("SRS-2026-1010", 2, "Khushi", "Joshi", "Female", "2009-10-10", "O+", "Class 11 (Sci)", "A", "Nitin Joshi", "Father", "+91 98112 00010", "nitin.j@gmail.com", "Professor"),
        ("SRS-2026-1011", 3, "Aryan", "Malhotra", "Male", "2009-05-19", "A-", "Class 11 (Sci)", "A", "Vivek Malhotra", "Father", "+91 98112 00011", "malhotra.v@gmail.com", "Industrialist"),
        ("SRS-2026-1012", 4, "Riya", "Bansal", "Female", "2009-12-01", "B+", "Class 11 (Sci)", "A", "Mukesh Bansal", "Father", "+91 98112 00012", "m.bansal@gmail.com", "Merchant"),

        ("SRS-2026-1013", 1, "Manav", "Chopra", "Male", "2008-03-21", "AB+", "Class 12 (Sci)", "A", "Alok Chopra", "Father", "+91 98112 00013", "alok.chopra@gmail.com", "Director"),
        ("SRS-2026-1014", 2, "Tanya", "Aggarwal", "Female", "2008-09-09", "O+", "Class 12 (Sci)", "A", "Sunil Aggarwal", "Father", "+91 98112 00014", "sunil.agg@gmail.com", "Businessman"),
        ("SRS-2026-1015", 3, "Yash", "Goyal", "Male", "2008-11-27", "B+", "Class 12 (Sci)", "A", "Praveen Goyal", "Father", "+91 98112 00015", "praveen.g@gmail.com", "Financial Analyst"),

        ("SRS-2026-1016", 1, "Vihaan", "Mishra", "Male", "2011-04-05", "B+", "Class 9", "A", "Rakesh Mishra", "Father", "+91 98112 00016", "r.mishra@gmail.com", "Consultant"),
        ("SRS-2026-1017", 2, "Myra", "Sethi", "Female", "2011-08-17", "A+", "Class 9", "A", "Gaurav Sethi", "Father", "+91 98112 00017", "gaurav.s@gmail.com", "Creative Director"),
        ("SRS-2026-1018", 1, "Reyansh", "Pandit", "Male", "2012-06-11", "O+", "Class 8", "A", "Hari Pandit", "Father", "+91 98112 00018", "hari.p@gmail.com", "Service"),
        ("SRS-2026-1019", 2, "Navya", "Trivedi", "Female", "2012-10-30", "B+", "Class 8", "A", "Anurag Trivedi", "Father", "+91 98112 00019", "anurag.t@gmail.com", "Educationist"),
        ("SRS-2026-1020", 1, "Shaurya", "Dubey", "Male", "2013-01-22", "AB-", "Class 7", "A", "Brijesh Dubey", "Father", "+91 98112 00020", "brijesh.d@gmail.com", "Manager"),
    ]

    students = []
    for adm, roll, fn, ln, gen, dob, bg, c_name, s_name, p_name, p_rel, p_ph, p_em, p_occ in student_data:
        c_obj = classes.get(c_name)
        s_obj = sections.get(f"{c_name}_{s_name}")
        if not c_obj or not s_obj:
            continue
        dob_date = datetime.datetime.strptime(dob, "%Y-%m-%d").date()
        st, created = Student.objects.get_or_create(
            admission_number=adm,
            defaults={
                'roll_number': roll,
                'first_name': fn,
                'last_name': ln,
                'gender': gen,
                'dob': dob_date,
                'blood_group': bg,
                'class_level': c_obj,
                'section': s_obj,
                'admission_date': datetime.date(2025, 4, 10),
                'parent_name': p_name,
                'parent_relation': p_rel,
                'parent_phone': p_ph,
                'parent_email': p_em,
                'parent_occupation': p_occ,
                'address': "SRS Residency, Sector 62, Noida, Delhi NCR",
                'emergency_contact': p_ph,
                'is_active': True,
            }
        )
        students.append(st)

    # 9. Attendance (last 5 days)
    today = timezone.now().date()
    statuses = ['Present', 'Present', 'Present', 'Present', 'Absent', 'Late']
    for day_offset in range(5):
        att_date = today - datetime.timedelta(days=day_offset)
        for s in students:
            # Consistent pseudo-random attendance
            st_val = statuses[(s.roll_number + day_offset) % len(statuses)]
            Attendance.objects.get_or_create(
                student=s,
                date=att_date,
                defaults={'status': st_val, 'remarks': 'Regular' if st_val == 'Present' else 'Reported'}
            )

    # 10. Fee Invoices & Payments
    t_fee = categories["Quarterly Tuition Fee"]
    dev_fee = categories["Annual Development Fee"]
    exam_fee = categories["Examination & Assessment Fee"]

    for idx, s in enumerate(students):
        # Invoice 1: Tuition Fee
        inv1, inv1_created = FeeInvoice.objects.get_or_create(
            invoice_number=f"INV-2026-{s.id:04d}-T1",
            student=s,
            defaults={
                'fee_category': t_fee,
                'academic_session': session,
                'amount': t_fee.default_amount,
                'discount': 1000.00 if s.roll_number == 1 else 0.00,
                'fine': 0.00,
                'due_date': today + datetime.timedelta(days=15),
                'status': 'Unpaid'
            }
        )
        if inv1_created and idx % 2 == 0:
            # Pay half or full
            paid_amt = inv1.total_payable
            pay1 = FeePayment.objects.create(
                receipt_number=f"REC-2026-{inv1.id:04d}-P1",
                invoice=inv1,
                amount_paid=paid_amt,
                payment_date=today - datetime.timedelta(days=idx % 7),
                payment_method='UPI / QR' if idx % 4 == 0 else 'Cash',
                transaction_reference=f"UPI-REF-{random.randint(10000000, 99999999)}",
                notes="Quarterly tuition fee cleared."
            )
            inv1.update_status()

        # Invoice 2: Development Fee
        if idx % 3 == 0:
            inv2, inv2_created = FeeInvoice.objects.get_or_create(
                invoice_number=f"INV-2026-{s.id:04d}-DEV",
                student=s,
                defaults={
                    'fee_category': dev_fee,
                    'academic_session': session,
                    'amount': dev_fee.default_amount,
                    'due_date': today - datetime.timedelta(days=5),
                    'status': 'Unpaid'
                }
            )
            inv2.update_status()

    # 11. Examinations & Marks
    exam, _ = Exam.objects.get_or_create(
        name="Mid-Term Examination 2026",
        defaults={
            'academic_session': session,
            'start_date': datetime.date(2026, 9, 10),
            'end_date': datetime.date(2026, 9, 25),
            'is_active': True,
            'is_published': True
        }
    )

    core_subjs = [subjects["MATH101"], subjects["ENG101"], subjects["PHY101"], subjects["CHEM101"], subjects["CS101"]]
    marks_pool = [94.5, 88.0, 76.5, 82.0, 91.0, 68.5, 85.0, 96.0, 72.0, 89.5]
    for s in students[:10]: # Seed top 10 students with complete marksheet
        for s_idx, subj in enumerate(core_subjs):
            score = marks_pool[(s.roll_number + s_idx) % len(marks_pool)]
            ExamResult.objects.get_or_create(
                exam=exam,
                student=s,
                subject=subj,
                defaults={
                    'marks_obtained': score,
                    'max_marks': 100.0,
                    'remarks': "Consistent understanding and good problem solving."
                }
            )

    # 12. Notices
    notice_list = [
        ("Annual Sports Meet 2026 - Registration Open", "The Annual Inter-House Sports Meet 2026 will be held from 15th October to 18th October at the main stadium ground. Interested students must submit their names to their sports house captain before Friday.", "All", True),
        ("Parent-Teacher Conference (PTM) Scheduled", "Parent-Teacher Interaction for Term 1 will take place this Saturday, 9:00 AM to 1:00 PM. Parents are cordially requested to review their ward's mid-term performance reports.", "All", False),
        ("Science & Robotics Exhibition 2026", "Submissions are open for our upcoming STEM & Robotics fair. Model display kits and project guidelines are available with the Computer Science & Physics departments.", "Students", False),
        ("Staff Welfare & Academic Review Meeting", "All Department Heads and Senior Faculty members are requested to assemble in Conference Hall A at 3:30 PM for the bi-monthly syllabus progress audit.", "Teachers", False),
    ]
    for n_title, n_content, n_aud, n_urg in notice_list:
        Notice.objects.get_or_create(
            title=n_title,
            defaults={
                'content': n_content,
                'target_audience': n_aud,
                'is_urgent': n_urg,
                'expiry_date': today + datetime.timedelta(days=30)
            }
        )

    print("SRS School ERP data successfully seeded!")
