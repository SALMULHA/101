from flask import Flask, render_template, redirect, url_for
from flask_login import current_user
from config import Config
from extensions import db, login_manager, csrf
from modules.models import User
import os
from logging_config import setup_logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # تهيئة قاعدة البيانات
    db.init_app(app)

    # تهيئة مدير تسجيل الدخول
    login_manager.init_app(app)

    # تهيئة CSRF protection
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # إنشاء مجلدات التطبيق إذا لم تكن موجودة
    with app.app_context():
        # إنشاء مجلد instance لقاعدة البيانات
        instance_path = os.path.join(app.config['BASEDIR'], 'instance')
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
            
        # إنشاء مجلد التحميلات إذا لم يكن موجوداً
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        # إنشاء قاعدة البيانات إذا لم تكن موجودة
        db.create_all()

    # استيراد البلوبرنتس
    from modules.auth import auth_bp
    from modules.personnel import personnel_bp
    from modules.attendance import attendance_bp
    from modules.reports import reports_bp
    from modules.admin import admin_bp
    from modules.notifications import notifications_bp

    # إضافة استيراد المجدول
    import scheduler

    # تسجيل البلوبرنتس
    app.register_blueprint(auth_bp)
    app.register_blueprint(personnel_bp)
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
    app.register_blueprint(reports_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notifications_bp)

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('auth.login'))

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.utcnow()}

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500

    return app

# للتحقق من المسارات المسجلة (أزل هذا بعد التأكد)
if __name__ == '__main__':
    app = create_app()
    setup_logging(app)
    print("المسارات المسجلة:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule}")
    app.run(debug=True)