from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import os
import tempfile
import pandas as pd
from extensions import db  # تغيير من app import db
from modules.models import Personnel, AttendanceRecord, AttendanceStatus, Department, Rank
from modules.decorators import department_admin_required, check_department_access
from modules.reports import reports_bp  # إضافة هذا السطر

# حذف السطر التالي لأنه تم تعريف البلوبرنت في __init__.py
# reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
@department_admin_required
def index():
    """الصفحة الرئيسية للتقارير"""
    # تطبيق قيود القسم
    if current_user.role.name == 'مسؤول قسم':
        departments = [current_user.department]  # فقط قسم المستخدم
    else:
        departments = Department.query.all()  # جميع الأقسام للمدير
    
    ranks = Rank.query.all()
    statuses = AttendanceStatus.query.all()
    
    return render_template('reports/index.html',
                          departments=departments,
                          ranks=ranks,
                          statuses=statuses)

@reports_bp.route('/daily')
@login_required
@department_admin_required
def daily_report():
    """تقرير التمام اليومي"""
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    department_id = request.args.get('department_id', type=int)
    export_format = request.args.get('format', 'html')
    
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # بناء الاستعلام مع تطبيق قيود القسم
        query = db.session.query(
            Personnel,
            AttendanceRecord,
            AttendanceStatus,
            Department,
            Rank
        ).join(
            AttendanceRecord, Personnel.id == AttendanceRecord.personnel_id, isouter=True
        ).join(
            AttendanceStatus, AttendanceRecord.status_id == AttendanceStatus.id, isouter=True
        ).join(
            Department, Personnel.department_id == Department.id
        ).join(
            Rank, Personnel.rank_id == Rank.id
        ).filter(
            (AttendanceRecord.date == selected_date) | (AttendanceRecord.date == None)
        )
        
        # تطبيق قيود القسم
        if current_user.role.name == 'مسؤول قسم':
            query = query.filter(Personnel.department_id == current_user.department_id)
            department_id = current_user.department_id  # فرض قسم المستخدم
        elif department_id and current_user.role.name == 'مدير':
            query = query.filter(Personnel.department_id == department_id)
        
        results = query.order_by(
            Department.name,
            Rank.id,
            Personnel.full_name
        ).all()
        
        # تجميع النتائج
        report_data = []
        for person, attendance, status, department, rank in results:
            report_data.append({
                'military_id': person.military_id,
                'full_name': person.full_name,
                'rank': rank.name,
                'department': department.name,
                'status': status.name if status else 'غير مسجل',
                'notes': attendance.notes if attendance else ''
            })
        
        # تصدير التقرير حسب التنسيق المطلوب
        if export_format == 'excel':
            df = pd.DataFrame(report_data)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            df.to_excel(temp_file.name, index=False, sheet_name='تقرير التمام اليومي')
            return send_file(temp_file.name, as_attachment=True, download_name=f'daily_report_{date_str}.xlsx')
        elif export_format == 'pdf':
            return render_template('reports/daily_pdf.html',
                                  date=selected_date,
                                  report_data=report_data)
        else:
            return render_template('reports/daily.html',
                                  date=selected_date,
                                  department_id=department_id,
                                  report_data=report_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@reports_bp.route('/summary')
@login_required
def summary_report():
    """تقرير ملخص التمام"""
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    export_format = request.args.get('format', 'html')
    
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # إحصائيات حسب القسم والحالة
        department_summary = db.session.query(
            Department.name.label('department'),
            AttendanceStatus.name.label('status'),
            db.func.count(Personnel.id).label('count')
        ).join(
            Personnel, Department.id == Personnel.department_id
        ).join(
            Attendance, Personnel.id == Attendance.personnel_id, isouter=True
        ).join(
            AttendanceStatus, Attendance.status_id == AttendanceStatus.id, isouter=True
        ).filter(
            (Attendance.date == selected_date) | (Attendance.date == None)
        ).group_by(
            Department.name,
            AttendanceStatus.name
        ).order_by(
            Department.name,
            AttendanceStatus.name
        ).all()
        
        # إحصائيات حسب الرتبة والحالة
        rank_summary = db.session.query(
            Rank.name.label('rank'),
            AttendanceStatus.name.label('status'),
            db.func.count(Personnel.id).label('count')
        ).join(
            Personnel, Rank.id == Personnel.rank_id
        ).join(
            Attendance, Personnel.id == Attendance.personnel_id, isouter=True
        ).join(
            AttendanceStatus, Attendance.status_id == AttendanceStatus.id, isouter=True
        ).filter(
            (Attendance.date == selected_date) | (Attendance.date == None)
        ).group_by(
            Rank.name,
            AttendanceStatus.name
        ).order_by(
            Rank.id,
            AttendanceStatus.name
        ).all()
        
        # تصدير التقرير حسب التنسيق المطلوب
        if export_format == 'excel':
            # إنشاء ملف Excel مؤقت
            dept_df = pd.DataFrame([(d.department, d.status, d.count) for d in department_summary],
                                  columns=['القسم', 'الحالة', 'العدد'])
            rank_df = pd.DataFrame([(r.rank, r.status, r.count) for r in rank_summary],
                                  columns=['الرتبة', 'الحالة', 'العدد'])
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            with pd.ExcelWriter(temp_file.name) as writer:
                dept_df.to_excel(writer, sheet_name='حسب القسم', index=False)
                rank_df.to_excel(writer, sheet_name='حسب الرتبة', index=False)
            
            return send_file(temp_file.name, as_attachment=True, download_name=f'summary_report_{date_str}.xlsx')
        elif export_format == 'pdf':
            # سيتم تنفيذ تصدير PDF لاحقاً
            return render_template('reports/summary_pdf.html',
                                  date=selected_date,
                                  department_summary=department_summary,
                                  rank_summary=rank_summary)
        else:
            # عرض التقرير كصفحة HTML
            return render_template('reports/summary.html',
                                  date=selected_date,
                                  department_summary=department_summary,
                                  rank_summary=rank_summary)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@reports_bp.route('/personnel')
@login_required
def personnel_report():
    """تقرير الأفراد"""
    department_id = request.args.get('department_id', type=int)
    rank_id = request.args.get('rank_id', type=int)
    status_id = request.args.get('status_id', type=int)
    export_format = request.args.get('format', 'html')
    
    try:
        # بناء الاستعلام
        query = db.session.query(
            Personnel,
            Department,
            Rank,
            AttendanceStatus
        ).join(
            Department, Personnel.department_id == Department.id
        ).join(
            Rank, Personnel.rank_id == Rank.id
        ).join(
            AttendanceStatus, Personnel.status_id == AttendanceStatus.id
        ).join(
            AttendanceRecord, Personnel.id == AttendanceRecord.personnel_id, isouter=True
        ).join(
            AttendanceStatus, AttendanceRecord.status_id == AttendanceStatus.id, isouter=True
        )
        
        if department_id:
            query = query.filter(Personnel.department_id == department_id)
        
        if rank_id:
            query = query.filter(Personnel.rank_id == rank_id)
        
        if status_id:
            query = query.filter(Personnel.status_id == status_id)
        
        results = query.order_by(
            Department.name,
            Rank.id,
            Personnel.full_name
        ).all()
        
        # تجميع النتائج
        report_data = []
        for person, department, rank, status in results:
            report_data.append({
                'military_id': person.military_id,
                'full_name': person.full_name,
                'rank': rank.name,
                'department': department.name,
                'status': status.name,
                'phone': person.phone,
                'notes': person.notes
            })
        
        # تصدير التقرير حسب التنسيق المطلوب
        if export_format == 'excel':
            # إنشاء ملف Excel مؤقت
            df = pd.DataFrame(report_data)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            df.to_excel(temp_file.name, index=False, sheet_name='تقرير الأفراد')
            return send_file(temp_file.name, as_attachment=True, download_name='personnel_report.xlsx')
        elif export_format == 'pdf':
            # سيتم تنفيذ تصدير PDF لاحقاً
            return render_template('reports/personnel_pdf.html',
                                  report_data=report_data)
        else:
            # عرض التقرير كصفحة HTML
            departments = Department.query.all()
            ranks = Rank.query.all()
            statuses = AttendanceStatus.query.all()
            
            return render_template('reports/personnel.html',
                                  department_id=department_id,
                                  rank_id=rank_id,
                                  status_id=status_id,
                                  departments=departments,
                                  ranks=ranks,
                                  statuses=statuses,
                                  report_data=report_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@reports_bp.route('/history/<int:personnel_id>')
@login_required
def history_report(personnel_id):
    """تقرير تاريخ حالات فرد"""
    person = Personnel.query.get_or_404(personnel_id)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    export_format = request.args.get('format', 'html')
    
    try:
        # تحديد الفترة الزمنية
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # الحصول على سجلات التمام
        attendance_records = db.session.query(
            Attendance,
            AttendanceStatus
        ).join(
            AttendanceStatus, Attendance.status_id == AttendanceStatus.id
        ).filter(
            Attendance.personnel_id == personnel_id,
            Attendance.date.between(start_date_obj, end_date_obj)
        ).order_by(
            Attendance.date.desc()
        ).all()
        
        # تجميع النتائج
        history_data = []
        for attendance, status in attendance_records:
            history_data.append({
                'date': attendance.date,
                'status': status.name,
                'notes': attendance.notes
            })
        
        # تصدير التقرير حسب التنسيق المطلوب
        if export_format == 'excel':
            # إنشاء ملف Excel مؤقت
            df = pd.DataFrame(history_data)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            df.to_excel(temp_file.name, index=False, sheet_name='تاريخ الحالات')
            return send_file(temp_file.name, as_attachment=True, download_name=f'history_{person.military_id}.xlsx')
        elif export_format == 'pdf':
            # سيتم تنفيذ تصدير PDF لاحقاً
            return render_template('reports/history_pdf.html',
                                  person=person,
                                  start_date=start_date,
                                  end_date=end_date,
                                  history_data=history_data)
        else:
            # عرض التقرير كصفحة HTML
            return render_template('reports/history.html',
                                  person=person,
                                  start_date=start_date,
                                  end_date=end_date,
                                  history_data=history_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400