from app import app, db
from modules.models import Role, User, Department, Rank, AttendanceStatus
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_db():
    with app.app_context():
        # إنشاء قاعدة البيانات
        db.create_all()
        
        # إضافة الأدوار إذا لم تكن موجودة
        roles = [
            {'name': 'مدير', 'description': 'صلاحيات كاملة للنظام'},
            {'name': 'مشرف', 'description': 'إدارة قسم محدد'},
            {'name': 'مستخدم', 'description': 'صلاحيات محدودة'}
        ]
        
        for role_data in roles:
            role = Role.query.filter_by(name=role_data['name']).first()
            if not role:
                role = Role(name=role_data['name'], description=role_data['description'])
                db.session.add(role)
        
        # إضافة الأقسام الافتراضية
        departments = [
            {'name': 'الإدارة', 'description': 'الإدارة العامة'},
            {'name': 'العمليات', 'description': 'قسم العمليات'},
            {'name': 'الأقلام', 'description': 'قسم الأقلام'},
            {'name': 'الأمن', 'description': 'قسم الأمن'},
            {'name': 'الإمداد', 'description': 'قسم الإمداد والتموين'}
        ]
        
        for dept_data in departments:
            dept = Department.query.filter_by(name=dept_data['name']).first()
            if not dept:
                dept = Department(name=dept_data['name'], description=dept_data['description'])
                db.session.add(dept)
        
        # إضافة الرتب
        ranks = [
            # ضباط
            {'name': 'لواء', 'category': 'ضابط'},
            {'name': 'عميد', 'category': 'ضابط'},
            {'name': 'عقيد', 'category': 'ضابط'},
            {'name': 'مقدم', 'category': 'ضابط'},
            {'name': 'رائد', 'category': 'ضابط'},
            {'name': 'نقيب', 'category': 'ضابط'},
            {'name': 'ملازم أول', 'category': 'ضابط'},
            {'name': 'ملازم', 'category': 'ضابط'},
            # ضباط صف
            {'name': 'مساعد', 'category': 'ضابط صف'},
            {'name': 'رقيب أول', 'category': 'ضابط صف'},
            {'name': 'رقيب', 'category': 'ضابط صف'},
            {'name': 'عريف', 'category': 'ضابط صف'},
            {'name': 'وكيل عريف', 'category': 'ضابط صف'},
            # جنود
            {'name': 'جندي', 'category': 'جندي'},
            # أخرى
            {'name': 'مدني', 'category': 'مساندة'},
            {'name': 'متعاقد', 'category': 'عقد'}
        ]
        
        for rank_data in ranks:
            rank = Rank.query.filter_by(name=rank_data['name']).first()
            if not rank:
                rank = Rank(name=rank_data['name'], category=rank_data['category'])
                db.session.add(rank)
        
        # إضافة حالات التمام
        statuses = [
            {'name': 'حاضر', 'description': 'موجود في التوكة', 'requires_document': False},
            {'name': 'غائب', 'description': 'غير موجود بدون إذن', 'requires_document': False},
            {'name': 'هروب', 'description': 'غائب لأكثر من 15 يوم', 'requires_document': True},
            {'name': 'إجازة', 'description': 'إجازة رسمية', 'requires_document': True},
            {'name': 'مأمورية', 'description': 'مأمورية رسمية', 'requires_document': True},
            {'name': 'انتداب', 'description': 'منتدب لجهة أخرى', 'requires_document': True},
            {'name': 'دورة', 'description': 'في دورة تدريبية', 'requires_document': True},
            {'name': 'راحة طبية', 'description': 'راحة طبية معتمدة', 'requires_document': True},
            {'name': 'مستشفى', 'description': 'منوم في المستشفى', 'requires_document': True},
            {'name': 'حبس', 'description': 'محبوس على ذمة قضية', 'requires_document': True},
            {'name': 'مفقود', 'description': 'مفقود ولا يعرف مكانه', 'requires_document': True},
            {'name': 'وفاة', 'description': 'متوفي', 'requires_document': True}
        ]
        
        for status_data in statuses:
            status = AttendanceStatus.query.filter_by(name=status_data['name']).first()
            if not status:
                status = AttendanceStatus(
                    name=status_data['name'],
                    description=status_data['description'],
                    requires_document=status_data['requires_document']
                )
                db.session.add(status)
        
        # إضافة مستخدم مدير افتراضي إذا لم يكن موجودًا
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_role = Role.query.filter_by(name='مدير').first()
            admin_dept = Department.query.filter_by(name='الإدارة').first()
            
            if admin_role and admin_dept:
                admin_user = User(
                    username='admin',
                    full_name='مدير النظام',
                    email='admin@example.com',
                    password_hash=generate_password_hash('admin'),  # تغيير من admin123 إلى admin
                    role_id=admin_role.id,
                    department_id=admin_dept.id,
                    is_active=True,
                    last_login=datetime.utcnow()
                )
                db.session.add(admin_user)
        
        # حفظ التغييرات
        db.session.commit()
        print('تم تهيئة قاعدة البيانات بنجاح!')

if __name__ == '__main__':
    init_db()