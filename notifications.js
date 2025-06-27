// دوال الإشعارات المحسنة
class NotificationManager {
    constructor() {
        this.baseUrl = '/notifications';
    }
    
    async markAsRead(notificationId) {
        try {
            const response = await fetch(`${this.baseUrl}/mark_read/${notificationId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error('فشل في تحديث الإشعار');
            }
            
            const data = await response.json();
            if (data.success) {
                this.updateNotificationUI(notificationId);
                this.updateUnreadCount(-1);
            }
        } catch (error) {
            console.error('خطأ:', error);
            this.showAlert('حدث خطأ أثناء تحديث الإشعار', 'danger');
        }
    }
    
    updateNotificationUI(notificationId) {
        const notification = document.getElementById(`notification-${notificationId}`);
        if (notification) {
            notification.classList.remove('list-group-item-light', 'border-start', 'border-4');
            const title = notification.querySelector('h6');
            if (title) title.classList.remove('fw-bold');
            const button = notification.querySelector('button');
            if (button) button.remove();
        }
    }
    
    updateUnreadCount(change) {
        const badge = document.querySelector('.navbar .badge');
        if (badge) {
            let count = parseInt(badge.textContent) + change;
            if (count > 0) {
                badge.textContent = count;
            } else {
                badge.remove();
            }
        }
    }
    
    showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => alertDiv.remove(), 5000);
    }
}

// تهيئة مدير الإشعارات
const notificationManager = new NotificationManager();