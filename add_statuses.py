from app import create_app
from extensions import db
from modules.models import AttendanceStatus

app = create_app()

with app.app_context():
    # قائمة الحالات المطلوبة
    statuses = [
        {"name": "حاضر", "description": "الفرد موجود في الوحدة", "requires_document": False},
        {"name": "غائب", "description": "الفرد غير موجود بدون إذن", "requires_document": False},
        {"name": "هروب", "description": "غياب لمدة تزيد عن 15 يوم", "requires_document": True},
        {"name": "انتداب داخل الوحدة", "description": "انتداب داخلي", "requires_document": True},
        {"name": "انتداب خارج الوحدة", "description": "انتداب خارجي", "requires_document": True},
        {"name": "دورة داخل ليبيا", "description": "دورة تدريبية داخل البلاد", "requires_document": True},
        {"name": "دورة خارج ليبيا", "description": "دورة تدريبية خارج البلاد", "requires_document": True},
        {"name": "مأمورية", "description": "مهمة رسمية", "requires_document": True},
        {"name": "مهمة خارجية", "description": "مهمة خارج الوحدة", "requires_document": True},
        {"name": "إجازة داخل ليبيا", "description": "إجازة داخل البلاد", "requires_document": True},
        {"name": "إجازة خارج ليبيا", "description": "إجازة خارج البلاد", "requires_document": True},
        {"name": "راحة عمل", "description": "راحة بعد فترة عمل", "requires_document": True},
        {"name": "مستشفى", "description": "تواجد في المستشفى", "requires_document": True},
        {"name": "سرية طبية", "description": "تحت الرعاية الطبية", "requires_document": True},
        {"name": "راحة طبية", "description": "راحة بسبب ظروف صحية", "requires_document": True},
        {"name": "علاج خارج ليبيا", "description": "علاج خارج البلاد", "requires_document": True},
        {"name": "ضبطية", "description": "قيد الضبطية", "requires_document": True},
        {"name": "محكمة عسكرية", "description": "إجراءات محكمة عسكرية", "requires_document": True},
        {"name": "محكمة مدنية", "description": "إجراءات محكمة مدنية", "requires_document": True},
        {"name": "دائمة وعليا", "description": "لجنة دائمة وعليا", "requires_document": True},
        {"name": "مفقود", "description": "الفرد مفقود", "requires_document": True},
        {"name": "وفاة", "description": "الفرد متوفي", "requires_document": True},
        {"name": "شهيد", "description": "استشهد في الخدمة", "requires_document": True},
        {"name": "جريح", "description": "أصيب أثناء الخدمة", "requires_document": True},
        {"name": "أسير", "description": "أسير حرب", "requires_document": True},
    ]
    
    # إضافة الحالات إذا لم تكن موجودة
    for status_data in statuses:
        existing_status = AttendanceStatus.query.filter_by(name=status_data["name"]).first()
        if not existing_status:
            new_status = AttendanceStatus(**status_data)
            db.session.add(new_status)
            print(f"تمت إضافة حالة: {status_data['name']}")
    
    db.session.commit()
    print("تم تحديث حالات التمام بنجاح")