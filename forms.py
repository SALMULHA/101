from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from modules.models import User
from modules.models import Role, Department

class LoginForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired()])
    password = PasswordField('كلمة المرور', validators=[DataRequired()])
    remember_me = BooleanField('تذكرني')
    submit = SubmitField('تسجيل الدخول')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('كلمة المرور الحالية', validators=[DataRequired()])
    new_password = PasswordField('كلمة المرور الجديدة', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('تغيير كلمة المرور')

class UserForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired(), Length(min=4, max=20)])
    full_name = StringField('الاسم الكامل', validators=[DataRequired(), Length(max=100)])
    email = StringField('البريد الإلكتروني', validators=[Email(), Length(max=120)])
    password = PasswordField('كلمة المرور')
    role_id = SelectField('الدور', coerce=int, validators=[DataRequired()])
    department_id = SelectField('القسم/الإدارة', coerce=int, validators=[Optional()])
    is_active = BooleanField('نشط', default=True)
    submit = SubmitField('حفظ')
    
    def __init__(self, *args, **kwargs):
        # استخراج user_id من kwargs إذا كان موجوداً
        self.user_id = kwargs.pop('user_id', None)
        super(UserForm, self).__init__(*args, **kwargs)
        self.role_id.choices = [(r.id, r.name) for r in Role.query.all()]
        # تحسين خيارات الأقسام مع إضافة الأقسام المذكورة
        departments = Department.query.all()
        self.department_id.choices = [(0, 'اختر القسم')] + [(d.id, d.name) for d in departments]
    
    def validate_department_id(self, field):
        # التحقق من أن مسؤول القسم لديه قسم محدد
        if self.role_id.data:
            role = Role.query.get(self.role_id.data)
            if role and role.name == 'مسؤول قسم':
                if not field.data or field.data == 0:
                    raise ValidationError('يجب تحديد قسم لمسؤول القسم - هذا إجباري لضمان الصلاحيات الصحيحة')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user and (not hasattr(self, 'user_id') or not self.user_id or user.id != self.user_id):
            raise ValidationError('اسم المستخدم مستخدم بالفعل. الرجاء اختيار اسم آخر.')