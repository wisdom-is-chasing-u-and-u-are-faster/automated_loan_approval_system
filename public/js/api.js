/**
 * SSMS Client API & DOM Interactivity Engine
 */

const SSMS_API = {
  baseUrl: '',

  getToken() {
    return localStorage.getItem('ssms_token') || '';
  },

  setToken(token, user) {
    localStorage.setItem('ssms_token', token);
    if (user) {
      localStorage.setItem('ssms_user', JSON.stringify(user));
    }
  },

  getUser() {
    const raw = localStorage.getItem('ssms_user');
    return raw ? JSON.parse(raw) : null;
  },

  logout() {
    localStorage.removeItem('ssms_token');
    localStorage.removeItem('ssms_user');
    window.location.href = '/pages/login.html';
  },

  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const res = await fetch(endpoint, {
        ...options,
        headers
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(errorData.detail || `Request failed with status ${res.status}`);
      }

      return await res.json();
    } catch (err) {
      console.error(`API Error on ${endpoint}:`, err);
      throw err;
    }
  },

  // Auth Endpoints
  async login(email, password, role) {
    const data = await this.request('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password, role })
    });
    this.setToken(data.token, data.user);
    return data;
  },

  async getMe() {
    return this.request('/api/v1/auth/me');
  },

  // Student Endpoints
  async getStudentDashboard() {
    return this.request('/api/v1/students/dashboard');
  },

  async getCourses(department = '', search = '') {
    let url = '/api/v1/courses';
    const params = new URLSearchParams();
    if (department) params.append('department', department);
    if (search) params.append('search', search);
    if (params.toString()) url += `?${params.toString()}`;
    return this.request(url);
  },

  async registerCourse(courseId) {
    return this.request('/api/v1/enrollments/register', {
      method: 'POST',
      body: JSON.stringify({ course_id: courseId })
    });
  },

  async getMyGrades() {
    return this.request('/api/v1/grades/my-grades');
  },

  // Faculty Endpoints
  async getFacultyCourses() {
    return this.request('/api/v1/faculty/courses');
  },

  async getGradebook(courseId) {
    return this.request(`/api/v1/faculty/courses/${courseId}/gradebook`);
  },

  async submitBulkGrades(courseId, grades) {
    return this.request('/api/v1/faculty/grades/bulk-submit', {
      method: 'POST',
      body: JSON.stringify({ course_id: courseId, grades })
    });
  },

  // Billing & Stripe
  async getInvoices() {
    return this.request('/api/v1/billing/invoices');
  },

  async createCheckoutSession(invoiceId, amount) {
    return this.request('/api/v1/billing/checkout-session', {
      method: 'POST',
      body: JSON.stringify({ invoice_id: invoiceId, amount, currency: 'usd' })
    });
  },

  // Transcripts
  async requestTranscript(recipientEmail, deliveryType = 'Electronic PDF', specialInstructions = '') {
    return this.request('/api/v1/transcripts/request', {
      method: 'POST',
      body: JSON.stringify({
        recipient_email: recipientEmail,
        delivery_type: deliveryType,
        special_instructions: specialInstructions
      })
    });
  },

  async getTranscriptRequests() {
    return this.request('/api/v1/transcripts/requests');
  },

  // Admin Endpoints
  async getAdminDashboard() {
    return this.request('/api/v1/admin/dashboard');
  },

  async getAuditLogs() {
    return this.request('/api/v1/admin/audit-logs');
  },

  async createCourse(courseData) {
    return this.request('/api/v1/courses', {
      method: 'POST',
      body: JSON.stringify(courseData)
    });
  }
};

window.SSMS_API = SSMS_API;
