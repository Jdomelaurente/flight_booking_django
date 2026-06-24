/**
 * Multi-Session Authentication Storage
 * File Location: bookingapp/src/utils/authStorage.js
 */

class AuthStorage {
  static initializeSession({ token, session_id, role, user, dashboard_route }) {
    let tabId = sessionStorage.getItem('tab_id')
    if (!tabId) {
      tabId = `tab_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      sessionStorage.setItem('tab_id', tabId)
    }

    sessionStorage.setItem('token', token)
    sessionStorage.setItem('auth_token', token)
    sessionStorage.setItem('session_id', session_id)
    sessionStorage.setItem('role', role)
    sessionStorage.setItem('user', JSON.stringify(user))
    sessionStorage.setItem('user_data', JSON.stringify(user))
    if (dashboard_route) sessionStorage.setItem('dashboard_route', dashboard_route)

    const sessionMetadata = {
      tabId, role, username: user.username, session_id, timestamp: Date.now()
    }

    const allSessions = this.getAllSessionsMetadata()
    allSessions[tabId] = sessionMetadata
    localStorage.setItem('active_sessions', JSON.stringify(allSessions))

    console.log('✅ Session initialized:', { tabId, role, username: user.username, total: Object.keys(allSessions).length })
    return tabId
  }

  static getToken() {
    return sessionStorage.getItem('token') || sessionStorage.getItem('auth_token') || localStorage.getItem('token') || localStorage.getItem('auth_token')
  }

  static getSessionId() {
    return sessionStorage.getItem('session_id') || localStorage.getItem('session_id')
  }

  static getRole() {
    return sessionStorage.getItem('role') || localStorage.getItem('role')
  }

  static getUser() {
    const userStr = sessionStorage.getItem('user') || sessionStorage.getItem('user_data') || localStorage.getItem('user') || localStorage.getItem('user_data')
    try {
      return userStr ? JSON.parse(userStr) : null
    } catch (e) {
      return null
    }
  }

  static getTabId() {
    return sessionStorage.getItem('tab_id')
  }

  static getAllSessionsMetadata() {
    try {
      const sessionsStr = localStorage.getItem('active_sessions')
      return sessionsStr ? JSON.parse(sessionsStr) : {}
    } catch (e) {
      return {}
    }
  }

  static isAuthenticated() {
    return !!(this.getToken() && this.getSessionId() && this.getRole())
  }

  static clearCurrentSession() {
    const tabId = this.getTabId()
    sessionStorage.clear()

    if (tabId) {
      const allSessions = this.getAllSessionsMetadata()
      delete allSessions[tabId]

      if (Object.keys(allSessions).length > 0) {
        localStorage.setItem('active_sessions', JSON.stringify(allSessions))
      } else {
        localStorage.removeItem('active_sessions')
      }
      console.log('🧹 Session cleared:', tabId, '| Remaining:', Object.keys(allSessions).length)
    }
  }

  static getAuthHeader() {
    const token = this.getToken()
    return token ? { 'Authorization': `Token ${token}` } : {}
  }

  static getApiHeaders() {
    return { ...this.getAuthHeader(), 'Content-Type': 'application/json', 'Accept': 'application/json' }
  }

  static getActiveSessions() {
    const metadata = this.getAllSessionsMetadata()
    return Object.entries(metadata).map(([tabId, data]) => ({
      tabId, ...data, isCurrent: tabId === this.getTabId()
    }))
  }

  static debugSessionState() {
    console.log('='.repeat(60))
    console.log('🔍 SESSION DEBUG')
    console.log('Tab ID:', this.getTabId())
    console.log('Authenticated:', this.isAuthenticated())
    console.log('Role:', this.getRole())
    console.log('User:', this.getUser()?.username)
    console.log('All Sessions:', this.getActiveSessions())
    console.log('='.repeat(60))
  }

  static cleanupStaleSessions() {
    const allSessions = this.getAllSessionsMetadata()
    const now = Date.now()
    const maxAge = 24 * 60 * 60 * 1000

    let cleaned = 0
    Object.keys(allSessions).forEach(tabId => {
      if (now - allSessions[tabId].timestamp > maxAge) {
        delete allSessions[tabId]
        cleaned++
      }
    })

    if (cleaned > 0) {
      if (Object.keys(allSessions).length > 0) {
        localStorage.setItem('active_sessions', JSON.stringify(allSessions))
      } else {
        localStorage.removeItem('active_sessions')
      }
    }
  }
}

AuthStorage.cleanupStaleSessions()

export default AuthStorage