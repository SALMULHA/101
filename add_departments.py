from app import app
from extensions import db
from modules.models import Department

def add_required_departments():
    """إضافة الأقسام المطلوبة للنظام"""
    departments = [
        {'name': 'الإدارة', 'description': 'قسم الإدارة العامة'},
        {'name': 'العمليات', 'description': 'قسم العمليات'},
        {'name': 'الأقلام', 'description': 'قسم الأقلام'},
        {'name': 'الأمن', 'description': 'قسم الأمن'},
        {'name': 'الإمداد والتموين', 'description': 'قسم الإمداد والتموين'}
    ]
    
    with app.app_context():
        for dept_data in departments:
            existing_dept = Department.query.filter_by(name=dept_data['name']).first()
            if not existing_dept:
                dept = Department(
                    name=dept_data['name'],
                    description=dept_data['description']
                )
                db.session.add(dept)
                print(f"تم إضافة قسم: {dept_data['name']}")
            else:
                print(f"القسم موجود بالفعل: {dept_data['name']}")
        
        db.session.commit()
        print("تم الانتهاء من إضافة الأقسام")

if __name__ == '__main__':
    add_required_departments()