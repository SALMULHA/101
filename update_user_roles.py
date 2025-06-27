from app import create_app
from extensions import db
from modules.models import User, Role

def update_existing_users():
    """تحديث أدوار المستخدمين الحاليين"""
    app = create_app()
    with app.app_context():
        # الحصول على الأدوار الجديدة
        system_admin_role = Role.query.filter_by(name='مدير النظام').first()
        department_admin_role = Role.query.filter_by(name='مدير قسم').first()
        
        if not system_admin_role:
            system_admin_role = Role.query.filter_by(name='مدير').first()
        
        if not department_admin_role:
            department_admin_role = Role.query.filter_by(name='مسؤول قسم').first()
        
        # تحديث المستخدمين الذين لديهم دور "مدير" القديم
        old_admin_users = User.query.join(Role).filter(Role.name == 'مدير').all()
        for user in old_admin_users:
            if system_admin_role:
                user.role_id = system_admin_role.id
                print(f"تم تحديث المستخدم {user.username} إلى مدير النظام")
        
        # تحديث المستخدمين الذين لديهم دور "مسؤول قسم" القديم
        old_dept_users = User.query.join(Role).filter(Role.name == 'مسؤول قسم').all()
        for user in old_dept_users:
            if department_admin_role:
                user.role_id = department_admin_role.id
                print(f"تم تحديث المستخدم {user.username} إلى مدير قسم")
        
        db.session.commit()
        print("تم تحديث جميع المستخدمين بنجاح")

if __name__ == '__main__':
    update_existing_users()