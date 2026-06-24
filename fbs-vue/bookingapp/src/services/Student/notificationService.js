import api from '../api/axios';

const notificationService = {
  /**
   * Fetch unread count and latest 20 notifications for the student.
   * @returns {Promise<Object>} { unread_count, notifications }
   */
  async getNotifications() {
    try {
      const response = await api.get('/api/student/notifications/');
      return response.data;
    } catch (error) {
      console.error('Error fetching notifications:', error);
      throw error;
    }
  },

  /**
   * Mark specific or all notifications as read.
   * @param {Array<Number>} notificationIds - Array of IDs to mark read. If empty/null, marks all as read.
   */
  async markAsRead(notificationIds = []) {
    try {
      const response = await api.patch('/api/student/notifications/mark-read/', {
        notification_ids: notificationIds
      });
      return response.data;
    } catch (error) {
      console.error('Error marking notifications as read:', error);
      throw error;
    }
  }
};

export default notificationService;
