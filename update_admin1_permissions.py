from modules.models import User, Role, Department
from app import create_app
from extensions import db

def update_admin1_permissions():
    app = create_app()
    with app.app_context():
        # البحث عن المستخدم admin1
        user = User.query.filter_by(username='admin1').first()
        if not user:
            print("المستخدم admin1 غير موجود")
            return
        
        # البحث عن دور المدير
        admin_role = Role.query.filter_by(name='مدير').first()
        if not admin_role:
            print("دور المدير غير موجود")
            return
        
        # تحديث دور المستخدم
        user.role_id = admin_role.id
        
        # إذا كنت تريد جعله مسؤول قسم بدلاً من مدير:
        # department_admin_role = Role.query.filter_by(name='مسؤول قسم').first()
        # user.role_id = department_admin_role.id
        # user.department_id = 1  # ضع رقم القسم المناسب
        
        db.session.commit()
        print(f"تم تحديث صلاحيات المستخدم {user.username} بنجاح")

if __name__ == '__main__':
    update_admin1_permissions()