import os

class Config:
    # إعدادات عامة
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'مفتاح-سري-افتراضي-للتطوير'
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    
    # إعدادات قاعدة البيانات
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASEDIR, 'instance', 'tmam.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # إعدادات تحميل الملفات
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 ميجابايت كحد أقصى