from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from extensions import db
from modules.models import AttendanceRecord, AttendanceStatus, Personnel, Notification, User
from sqlalchemy import and_
import atexit
import requests

def check_status_expiry_daily():
    """مهمة يومية لفحص انتهاء مدد الحالات"""
    from app import create_app
    
    app = create_app()
    with app.app_context():
        try:
            today = datetime.now().date()
            notifications_created = 0
            
            # الحالات المطلوب مراقبتها
            monitored_statuses = [
                'مأمورية',
                'إجازة داخل ليبيا', 
                'إجازة خارج ليبيا',
                'راحة عمل'
            ]
            
            for status_name in monitored_statuses:
                status = AttendanceStatus.query.filter_by(name=status_name).first()
                if not status:
                    continue
                    
                # البحث عن السجلات التي انتهت مدتها اليوم أو ستنتهي خلال 3 أيام
                expiring_records = AttendanceRecord.query.join(Personnel).filter(
                    AttendanceRecord.status_id == status.id,
                    AttendanceRecord.end_date.isnot(None),
                    AttendanceRecord.end_date <= today + timedelta(days=3),
                    AttendanceRecord.end_date >= today,
                    Personnel.is_active == True
                ).all()
                
                for record in expiring_records:
                    days_remaining = (record.end_date - today).days
                    
                    # التحقق من عدم وجود إشعار مماثل في آخر يوم
                    existing_notification = Notification.query.filter(
                        and_(
                            Notification.personnel_id == record.personnel_id,
                            Notification.created_at >= today - timedelta(days=1),
                            Notification.title.contains(f'انتهاء {status_name}')
                        )
                    ).first()
                    
                    if not existing_notification:
                        # تحديد نوع الإشعار حسب الأيام المتبقية
                        if days_remaining == 0:
                            notification_type = 'danger'
                            title = f'انتهت مدة {status_name} للفرد {record.personnel.full_name}'
                            message = f'انتهت اليوم مدة {status_name} للفرد {record.personnel.full_name} (الرقم العسكري: {record.personnel.military_id}). يرجى تحديث حالة الفرد.'
                        elif days_remaining == 1:
                            notification_type = 'warning'
                            title = f'ستنتهي غداً مدة {status_name} للفرد {record.personnel.full_name}'
                            message = f'ستنتهي غداً مدة {status_name} للفرد {record.personnel.full_name} (الرقم العسكري: {record.personnel.military_id}). يرجى الاستعداد لتحديث حالة الفرد.'
                        else:
                            notification_type = 'info'
                            title = f'ستنتهي خلال {days_remaining} أيام مدة {status_name} للفرد {record.personnel.full_name}'
                            message = f'ستنتهي خلال {days_remaining} أيام مدة {status_name} للفرد {record.personnel.full_name} (الرقم العسكري: {record.personnel.military_id}).'
                        
                        # إنشاء إشعار للمدراء
                        admin_users = User.query.join(User.role).filter(
                            User.role.has(name='admin')
                        ).all()
                        
                        for admin in admin_users:
                            notification = Notification(
                                title=title,
                                message=message,
                                notification_type=notification_type,
                                personnel_id=record.personnel_id,
                                user_id=admin.id,
                                is_system_generated=True
                            )
                            db.session.add(notification)
                            notifications_created += 1
            
            db.session.commit()
            print(f'تم إنشاء {notifications_created} إشعار لانتهاء المدد')
            
        except Exception as e:
            db.session.rollback()
            print(f'خطأ في فحص انتهاء المدد: {str(e)}')

def check_personnel_statuses_job():
    """مهمة فحص حالات الأفراد التلقائية"""
    from app import create_app
    
    app = create_app()
    with app.app_context():
        try:
            response = requests.get('http://127.0.0.1:5000/notifications/auto_check_statuses')
            if response.status_code == 200:
                print(f"تم فحص حالات الأفراد: {response.json()}")
            else:
                print(f"خطأ في فحص حالات الأفراد: {response.status_code}")
        except Exception as e:
            print(f"خطأ في مهمة فحص حالات الأفراد: {e}")

# إنشاء المجدول
scheduler = BackgroundScheduler()

# إضافة مهمة يومية في الساعة 8:00 صباحاً
scheduler.add_job(
    func=check_status_expiry_daily,
    trigger=CronTrigger(hour=8, minute=0),
    id='check_status_expiry',
    name='فحص انتهاء مدد الحالات',
    replace_existing=True
)

# إضافة المهمة للمجدول (كل 6 ساعات)
scheduler.add_job(
    func=check_personnel_statuses_job,
    trigger="interval",
    hours=6,
    id='check_personnel_statuses'
)

# بدء المجدول
scheduler.start()

# إيقاف المجدول عند إغلاق التطبيق
atexit.register(lambda: scheduler.shutdown())