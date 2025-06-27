// منظومة التمام - الوظائف الرئيسية

// تهيئة التلميحات
document.addEventListener('DOMContentLoaded', function() {
    // تفعيل tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })

    // تفعيل popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    })

    // إخفاء رسائل التنبيه تلقائيًا بعد 5 ثوانٍ
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);
});

// دالة تأكيد الحذف
function confirmDelete(message, formId) {
    if (confirm(message || 'هل أنت متأكد من الحذف؟')) {
        document.getElementById(formId).submit();
    }
    return false;
}

// دالة تحديث حالة التمام
function updateAttendanceStatus(personnelId, statusId, date) {
    fetch('/attendance/update_status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
        },
        body: JSON.stringify({
            personnel_id: personnelId,
            status_id: statusId,
            date: date
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // تحديث واجهة المستخدم
            const statusCell = document.querySelector(`#status-${personnelId}`);
            if (statusCell) {
                statusCell.textContent = data.status_name;
                statusCell.className = `status-${statusId}`;
                
                // تحديث الإحصائيات
                const presentCount = document.querySelector('#present-count');
                const absentCount = document.querySelector('#absent-count');
                if (presentCount && absentCount) {
                    if (statusId === 1) { // حاضر
                        presentCount.textContent = parseInt(presentCount.textContent) + 1;
                        absentCount.textContent = parseInt(absentCount.textContent) - 1;
                    } else {
                        presentCount.textContent = parseInt(presentCount.textContent) - 1;
                        absentCount.textContent = parseInt(absentCount.textContent) + 1;
                    }
                }
            }
        } else {
            alert('حدث خطأ: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('حدث خطأ أثناء تحديث الحالة');
    });
}

// دالة تحميل بيانات الأفراد حسب القسم
function loadPersonnelByDepartment(departmentId) {
    const url = `/personnel/list?department_id=${departmentId}`;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#personnel-table tbody');
            tableBody.innerHTML = '';
            
            data.forEach(person => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${person.military_id}</td>
                    <td>${person.full_name}</td>
                    <td>${person.rank}</td>
                    <td>${person.department}</td>
                    <td>
                        <a href="/personnel/view/${person.id}" class="btn btn-sm btn-info btn-action" data-bs-toggle="tooltip" title="عرض">
                            <i class="fas fa-eye"></i>
                        </a>
                        <a href="/personnel/edit/${person.id}" class="btn btn-sm btn-primary btn-action" data-bs-toggle="tooltip" title="تعديل">
                            <i class="fas fa-edit"></i>
                        </a>
                        <button onclick="confirmDelete('هل أنت متأكد من حذف هذا الفرد؟', 'delete-form-${person.id}')" class="btn btn-sm btn-danger btn-action" data-bs-toggle="tooltip" title="حذف">
                            <i class="fas fa-trash"></i>
                        </button>
                        <form id="delete-form-${person.id}" action="/personnel/delete/${person.id}" method="POST" style="display: none;">
                            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                        </form>
                    </td>
                `;
                tableBody.appendChild(row);
            });
            
            // إعادة تهيئة tooltips
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl)
            })
        })
        .catch(error => {
            console.error('Error:', error);
            alert('حدث خطأ أثناء تحميل البيانات');
        });
}