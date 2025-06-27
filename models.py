# تغيير من
# from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy()

# إلى
from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# حذف السطر db = SQLAlchemy() لأنه تم استيراد db من extensions

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_unread_notifications_count(self):
        from modules.models import Notification
        return Notification.query.filter_by(user_id=self.id, is_read=False).count()

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    personnel = db.relationship('Personnel', backref='department', lazy='dynamic')
    users = db.relationship('User', backref='department', lazy='dynamic')
    
    def __repr__(self):
        return f'<Department {self.name}>'

class Rank(db.Model):
    __tablename__ = 'ranks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50))  # ضابط، ضابط صف، جندي، عقد، مساندة
    personnel = db.relationship('Personnel', backref='rank', lazy='dynamic')
    
    def __repr__(self):
        return f'<Rank {self.name}>'

class Personnel(db.Model):
    __tablename__ = 'personnel'
    id = db.Column(db.Integer, primary_key=True)
    military_id = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    rank_id = db.Column(db.Integer, db.ForeignKey('ranks.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    # إضافة حقل status_id
    status_id = db.Column(db.Integer, db.ForeignKey('attendance_statuses.id'))
    status = db.relationship('AttendanceStatus', backref='personnel_status', foreign_keys=[status_id])
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    date_of_joining = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    attendance_records = db.relationship('AttendanceRecord', backref='personnel', lazy='dynamic')
    
    def __repr__(self):
        return f'<Personnel {self.military_id} - {self.full_name}>'

class AttendanceStatus(db.Model):
    __tablename__ = 'attendance_statuses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    requires_document = db.Column(db.Boolean, default=False)
    records = db.relationship('AttendanceRecord', backref='status', lazy='dynamic')
    
    def __repr__(self):
        return f'<AttendanceStatus {self.name}>'

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    id = db.Column(db.Integer, primary_key=True)
    personnel_id = db.Column(db.Integer, db.ForeignKey('personnel.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('attendance_statuses.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_date = db.Column(db.Date)  # تاريخ بداية الحالة (مثل بداية الإجازة)
    end_date = db.Column(db.Date)  # تاريخ نهاية الحالة (مثل نهاية الإجازة)
    document_path = db.Column(db.String(255))  # مسار المستند المرفق
    notes = db.Column(db.Text)
    # إضافة حقول جديدة لتتبع مصدر الحالة
    source_type = db.Column(db.String(20), default='manual')  # manual, copied, default
    source_date = db.Column(db.Date)  # التاريخ الذي تم النسخ منه
    is_auto_copied = db.Column(db.Boolean, default=False)  # هل تم النسخ تلقائياً
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # من قام بالتسجيل
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AttendanceRecord {self.personnel_id} - {self.date}>'

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)  # بالبايت
    attendance_record_id = db.Column(db.Integer, db.ForeignKey('attendance_records.id'))
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Document {self.original_filename}>'

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(50), nullable=False)  # مثل: إضافة، تعديل، حذف
    table_name = db.Column(db.String(50), nullable=False)  # اسم الجدول المتأثر
    record_id = db.Column(db.Integer)  # معرف السجل المتأثر
    old_values = db.Column(db.Text)  # القيم القديمة (JSON)
    new_values = db.Column(db.Text)  # القيم الجديدة (JSON)
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AuditLog {self.action} - {self.table_name} - {self.record_id}>'

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # warning, info, danger, success
    personnel_id = db.Column(db.Integer, db.ForeignKey('personnel.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # المستخدم المستهدف
    is_read = db.Column(db.Boolean, default=False)
    is_system_generated = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    
    # العلاقات
    personnel = db.relationship('Personnel', backref='notifications')
    user = db.relationship('User', backref='notifications')
    
    # إضافة فهارس لتحسين الأداء
    __table_args__ = (
        db.Index('idx_user_read', 'user_id', 'is_read'),
        db.Index('idx_personnel_created', 'personnel_id', 'created_at'),
        db.Index('idx_type_created', 'notification_type', 'created_at'),
    )
    def __repr__(self):
        return f'<Notification {self.title}>'
    
    def mark_as_read(self):
        self.is_read = True
        self.read_at = datetime.utcnow()
        db.session.commit()