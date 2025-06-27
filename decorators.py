from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user

def system_admin_required(f):
    """ديكوريتر للتحقق من صلاحيات مدير النظام"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('يجب تسجيل الدخول أولاً', 'danger')
            return redirect(url_for('auth.login'))
        
        if current_user.role.name not in ['مدير النظام', 'مدير']:
            flash('ليس لديك صلاحية للوصول إلى هذه الصفحة - مطلوب صلاحيات مدير النظام', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """ديكوريتر للتوافق مع النظام القديم - يستخدم system_admin_required"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('يجب تسجيل الدخول أولاً', 'danger')
            return redirect(url_for('auth.login'))
        
        if current_user.role.name not in ['مدير النظام', 'مدير']:
            flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def department_admin_required(f):
    """ديكوريتر للتحقق من صلاحيات مدير القسم أو مدير النظام"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('يجب تسجيل الدخول أولاً', 'danger')
            return redirect(url_for('auth.login'))
        
        allowed_roles = ['مدير النظام', 'مدير قسم', 'مدير', 'مسؤول قسم']
        if current_user.role.name not in allowed_roles:
            flash('ليس لديك صلاحية للوصول إلى هذه الصفحة - مطلوب صلاحيات مدير قسم على الأقل', 'danger')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def check_department_access(personnel_id=None, department_id=None):
    """التحقق من صلاحية الوصول للقسم"""
    # مدير النظام له صلاحية الوصول لكل شيء
    if current_user.role.name in ['مدير النظام', 'مدير']:
        return True
    
    # مدير القسم له صلاحية الوصول لقسمه فقط
    if current_user.role.name in ['مدير قسم', 'مسؤول قسم']:
        if not current_user.department_id:
            return False
            
        if department_id:
            return current_user.department_id == department_id
        
        if personnel_id:
            from modules.models import Personnel
            personnel = Personnel.query.get(personnel_id)
            if personnel:
                return current_user.department_id == personnel.department_id
    
    return False

def filter_by_department_access(query, model_class):
    """فلترة الاستعلام حسب صلاحيات القسم"""
    # مدير النظام يرى كل شيء
    if current_user.role.name in ['مدير النظام', 'مدير']:
        return query
    
    # مدير القسم يرى قسمه فقط
    if current_user.role.name in ['مدير قسم', 'مسؤول قسم']:
        if current_user.department_id:
            return query.filter(model_class.department_id == current_user.department_id)
        else:
            # إذا لم يكن له قسم محدد، لا يرى أي شيء
            return query.filter(False)
    
    # المستخدم العادي لا يرى أي شيء (أو حسب الصلاحيات المطلوبة)
    return query.filter(False)