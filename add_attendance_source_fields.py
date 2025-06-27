from extensions import db
from app import app
import sqlite3
import os

def add_attendance_source_fields():
    """إضافة حقول تتبع مصدر الحالة لجدول attendance_records"""
    with app.app_context():
        try:
            # الحصول على مسار قاعدة البيانات
            db_path = os.path.join(app.instance_path, 'tmam.db')
            
            # الاتصال بقاعدة البيانات مباشرة
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # التحقق من وجود الحقول أولاً
            cursor.execute("PRAGMA table_info(attendance_records)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # إضافة الحقول الجديدة إذا لم تكن موجودة
            if 'source_type' not in columns:
                cursor.execute("""
                    ALTER TABLE attendance_records 
                    ADD COLUMN source_type VARCHAR(20) DEFAULT 'manual'
                """)
                print("تم إضافة حقل source_type")
            
            if 'source_date' not in columns:
                cursor.execute("""
                    ALTER TABLE attendance_records 
                    ADD COLUMN source_date DATE
                """)
                print("تم إضافة حقل source_date")
            
            if 'is_auto_copied' not in columns:
                cursor.execute("""
                    ALTER TABLE attendance_records 
                    ADD COLUMN is_auto_copied BOOLEAN DEFAULT 0
                """)
                print("تم إضافة حقل is_auto_copied")
            
            if 'recorded_by' not in columns:
                cursor.execute("""
                    ALTER TABLE attendance_records 
                    ADD COLUMN recorded_by INTEGER
                """)
                print("تم إضافة حقل recorded_by")
                
                # نسخ البيانات من created_by إلى recorded_by إذا كان موجوداً
                if 'created_by' in columns:
                    cursor.execute("""
                        UPDATE attendance_records 
                        SET recorded_by = created_by 
                        WHERE created_by IS NOT NULL
                    """)
                    print("تم نسخ البيانات من created_by إلى recorded_by")
            
            # حفظ التغييرات
            conn.commit()
            conn.close()
            
            print("تم إضافة جميع حقول تتبع مصدر الحالة بنجاح")
            
        except Exception as e:
            print(f"خطأ في إضافة الحقول: {e}")
            if 'conn' in locals():
                conn.close()

if __name__ == '__main__':
    add_attendance_source_fields()