from app import app
from extensions import db
from modules.models import Personnel, AttendanceRecord, AttendanceStatus, Department, Rank
from datetime import datetime, timedelta
import random

def add_sample_personnel():
    """إضافة بيانات تجريبية للأفراد"""
    with app.app_context():
        # التحقق من وجود الأقسام والرتب
        departments = Department.query.all()
        ranks = Rank.query.all()
        statuses = AttendanceStatus.query.all()
        
        if not departments or not ranks or not statuses:
            print("يجب تشغيل init_db.py أولاً لإنشاء الأقسام والرتب والحالات")
            return
        
        # بيانات تجريبية للأفراد
        sample_personnel = [
            {'military_id': '12345', 'full_name': 'أحمد محمد علي', 'rank_id': 1, 'department_id': 1},
            {'military_id': '12346', 'full_name': 'محمد أحمد حسن', 'rank_id': 2, 'department_id': 1},
            {'military_id': '12347', 'full_name': 'علي حسن محمد', 'rank_id': 3, 'department_id': 2},
            {'military_id': '12348', 'full_name': 'حسن علي أحمد', 'rank_id': 4, 'department_id': 2},
            {'military_id': '12349', 'full_name': 'سعد محمد علي', 'rank_id': 5, 'department_id': 3},
            {'military_id': '12350', 'full_name': 'خالد أحمد سعد', 'rank_id': 6, 'department_id': 3},
            {'military_id': '12351', 'full_name': 'عبدالله محمد حسن', 'rank_id': 7, 'department_id': 4},
            {'military_id': '12352', 'full_name': 'فهد علي محمد', 'rank_id': 8, 'department_id': 4},
            {'military_id': '12353', 'full_name': 'عبدالعزيز حسن علي', 'rank_id': 9, 'department_id': 5},
            {'military_id': '12354', 'full_name': 'سلطان أحمد محمد', 'rank_id': 10, 'department_id': 5},
        ]
        
        # إضافة الأفراد
        for person_data in sample_personnel:
            existing = Personnel.query.filter_by(military_id=person_data['military_id']).first()
            if not existing:
                person = Personnel(
                    military_id=person_data['military_id'],
                    full_name=person_data['full_name'],
                    rank_id=person_data['rank_id'],
                    department_id=person_data['department_id'],
                    status_id=1,  # حاضر
                    is_active=True
                )
                db.session.add(person)
        
        db.session.commit()
        print(f"تم إضافة {len(sample_personnel)} فرد تجريبي")
        
        # إضافة سجلات تمام للأيام الماضية
        add_sample_attendance_records()

def add_sample_attendance_records():
    """إضافة سجلات تمام تجريبية"""
    personnel_list = Personnel.query.all()
    statuses = AttendanceStatus.query.all()
    
    if not personnel_list:
        print("لا توجد أفراد في قاعدة البيانات")
        return
    
    # إضافة سجلات للأيام الـ 30 الماضية
    for i in range(30):
        date = datetime.now().date() - timedelta(days=i)
        
        for person in personnel_list:
            # التحقق من عدم وجود سجل لهذا التاريخ
            existing_record = AttendanceRecord.query.filter_by(
                personnel_id=person.id,
                date=date
            ).first()
            
            if not existing_record:
                # اختيار حالة عشوائية (80% حاضر، 20% حالات أخرى)
                if random.random() < 0.8:
                    status_id = 1  # حاضر
                else:
                    status_id = random.choice([2, 4, 5, 8])  # غائب، إجازة، مأمورية، راحة طبية
                
                record = AttendanceRecord(
                    personnel_id=person.id,
                    date=date,
                    status_id=status_id,
                    notes=f"سجل تجريبي لتاريخ {date}",
                    source_type='manual',
                    is_auto_copied=False,
                    recorded_by=1  # مدير النظام
                )
                db.session.add(record)
    
    db.session.commit()
    print("تم إضافة سجلات التمام التجريبية للأيام الـ 30 الماضية")

if __name__ == '__main__':
    add_sample_personnel()