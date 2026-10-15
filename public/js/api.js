/**
 * Enterprise Automatic Loan Approval System (ALAS) - Client API Service
 * Handles asynchronous REST communication with /api/v1/* endpoints
 */

const API_BASE = '/api/v1';

const ALAS_API = {
  // --- Token / Auth Simulation ---
  getToken() {
    return localStorage.getItem('alas_token') || '';
  },

  setToken(token) {
    localStorage.setItem('alas_token', token);
  },

  getHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  },

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const opts = {
      headers: this.getHeaders(),
      ...options
    };

    try {
      const response = await fetch(url, opts);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `Request failed with status ${response.status}`);
      }
      return await response.json();
    } catch (err) {
      console.warn(`[ALAS API] Error on ${endpoint}:`, err);
      throw err;
    }
  },

  // --- Dashboard & Metrics ---
  async getDashboardMetrics() {
    return this.request('/dashboard/metrics');
  },

  async getVolumeHistory() {
    return this.request('/dashboard/volume-history');
  },

  // --- Loan Applications ---
  async getApplications(status = 'ALL', search = '') {
    let query = `?status=${encodeURIComponent(status)}`;
    if (search) query += `&search=${encodeURIComponent(search)}`;
    return this.request(`/applications${query}`);
  },

  async getApplicationDetails(appId) {
    return this.request(`/applications/${encodeURIComponent(appId)}`);
  },

  async submitApplication(applicationData) {
    return this.request('/applications', {
      method: 'POST',
      body: JSON.stringify(applicationData)
    });
  },

  async adjudicateApplication(appId, action, reviewNotes) {
    return this.request(`/applications/${encodeURIComponent(appId)}/adjudicate`, {
      method: 'POST',
      body: JSON.stringify({ action, review_notes: reviewNotes })
    });
  },

  async getManualReviewQueue() {
    return this.request('/applications/queue/manual-review');
  },

  // --- Reports & Analytics ---
  async getReports(reportType = 'daily_summary', startDate = '2024-07-01', endDate = '2024-07-21') {
    return this.request(`/reports?report_type=${encodeURIComponent(reportType)}&start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`);
  },

  // --- User & Role Management ---
  async getUsers() {
    return this.request('/users');
  },

  async createUser(userData) {
    return this.request('/users', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
  },

  async updateUser(userId, userData) {
    return this.request(`/users/${encodeURIComponent(userId)}`, {
      method: 'PUT',
      body: JSON.stringify(userData)
    });
  },

  // --- UI Helpers ---
  formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
  },

  getStatusBadgeClass(status) {
    const s = (status || '').toUpperCase();
    if (s.includes('APPROV')) return 'badge-approved';
    if (s.includes('REJECT') || s.includes('DEN')) return 'badge-rejected';
    if (s.includes('MANUAL')) return 'badge-manual';
    return 'badge-pending';
  }
};
