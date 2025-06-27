CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read);
CREATE INDEX idx_notifications_personnel_created ON notifications(personnel_id, created_at);
CREATE INDEX idx_notifications_type_created ON notifications(notification_type, created_at);