from app import create_app
from extensions import db
from modules.models import Role

def add_department_roles():
    app = create_app()
    with app.app_context():
        # تحديث دور مدير النظام
        system_admin_role = Role.query.filter_by(name='مدير النظام').first()
        if not system_admin_role:
            # البحث عن الدور القديم وتحديثه
            old_admin_role = Role.query.filter_by(name='مدير').first()
            if old_admin_role:
                old_admin_role.name = 'مدير النظام'
                old_admin_role.description = 'مدير النظام - له صلاحيات كاملة على جميع الأقسام والأفراد'
            else:
                system_admin_role = Role(
                    name='مدير النظام',
                    description='مدير النظام - له صلاحيات كاملة على جميع الأقسام والأفراد'
                )
                db.session.add(system_admin_role)
        
        # تحديث دور مدير القسم
        department_admin_role = Role.query.filter_by(name='مدير قسم').first()
        if not department_admin_role:
            # البحث عن الدور القديم وتحديثه
            old_dept_role = Role.query.filter_by(name='مسؤول قسم').first()
            if old_dept_role:
                old_dept_role.name = 'مدير قسم'
                old_dept_role.description = 'مدير قسم - له صلاحيات تسجيل التمام لأفراد قسمه فقط'
            else:
                department_admin_role = Role(
                    name='مدير قسم',
                    description='مدير قسم - له صلاحيات تسجيل التمام لأفراد قسمه فقط'
                )
                db.session.add(department_admin_role)
        
        # الاحتفاظ بدور المستخدم العادي
        user_role = Role.query.filter_by(name='مستخدم').first()
        if not user_role:
            user_role = Role(
                name='مستخدم',
                description='مستخدم عادي - صلاحيات اطلاع فقط'
            )
            db.session.add(user_role)
        
        db.session.commit()
        print("تم تحديث الأدوار بنجاح:")
        print("- مدير النظام: صلاحيات كاملة على جميع الأقسام")
        print("- مدير قسم: صلاحيات تسجيل التمام لقسمه فقط")
        print("- مستخدم: صلاحيات اطلاع فقط")

if __name__ == '__main__':
    add_department_roles()