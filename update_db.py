from app import app, db
import sqlite3

def update_database():
    with app.app_context():
        try:
            # استخدام sqlite3 مباشرة لتنفيذ أمر ALTER TABLE
            conn = sqlite3.connect('instance/tmam.db')
            cursor = conn.cursor()
            cursor.execute('ALTER TABLE personnel ADD COLUMN status_id INTEGER REFERENCES attendance_statuses(id)')
            conn.commit()
            conn.close()
            print("تم تحديث قاعدة البيانات بنجاح!")
        except Exception as e:
            print(f"حدث خطأ أثناء تحديث قاعدة البيانات: {str(e)}")

if __name__ == "__main__":
    update_database()