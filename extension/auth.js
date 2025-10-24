class AuthManager {
  constructor() {
    this.SCOPES = ['https://www.googleapis.com/auth/calendar.events'];
    this.CLIENT_ID = '852615838189-b88rr3ntne7hpf6f7t6k44mei2p2nm7u.apps.googleusercontent.com';
    this.AGENT_URL = 'https://datemark-dev-852615838189.europe-west1.run.app';
  }

  /**
   * Get Google OAuth token using Chrome Identity API
   * This leverages the user's existing Google sign-in
   */
  async getGoogleAuthToken(interactive = false) {
    return new Promise((resolve, reject) => {
      chrome.identity.getAuthToken({ interactive }, (token) => {
        if (chrome.runtime.lastError) {
          reject(chrome.runtime.lastError);
        } else {
          resolve(token);
        }
      });
    });
  }

  /**
   * Silent authentication - tries to get token without user interaction
   */
  async silentAuth() {
    try {
      const token = await this.getGoogleAuthToken(false);
      return { success: true, token };
    } catch (error) {
      return { success: false, error };
    }
  }

  /**
   * Interactive authentication - shows OAuth consent screen
   */
  async interactiveAuth() {
    try {
      const token = await this.getGoogleAuthToken(true);
      return { success: true, token };
    } catch (error) {
      return { success: false, error };
    }
  }

  /**
   * Revoke token and clear cache
   */
  async logout() {
    return new Promise((resolve, reject) => {
      chrome.identity.getAuthToken({ interactive: false }, (token) => {
        if (token) {
          chrome.identity.removeCachedAuthToken({ token }, () => {
            chrome.storage.local.remove(['identityToken', 'identityTokenExpiry'], () => {
              resolve();
            });
          });
        } else {
          chrome.storage.local.remove(['identityToken', 'identityTokenExpiry'], () => {
            resolve();
          });
        }
      });
    });
  }

  /**
   * Call Cloud Run function with identity token
   */
  async callCloudRun(endpoint, data) {
    try {
      const oauthToken = await this.getGoogleAuthToken(true);

      const response = await fetch(`${this.AGENT_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${oauthToken}`
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        // Handle quota exceeded error specifically
        if (response.status === 429) {
          const errorData = await response.json();
          const errorMessage = errorData.detail || "Period quota exceeded. Please upgrade your plan.";

          throw new Error(errorMessage);
        }

        // Handle other errors
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || `Cloud Run request failed: ${response.status}`;
        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      console.error('Error calling Cloud Run:', error);
      throw error;
    }
  }

  /**
   * Add events to Google Calendar
   */
  async addToCalendar(events) {
    try {
      const token = await this.getGoogleAuthToken(false);

      const results = [];
      for (const event of events) {
        const response = await fetch(
          'https://www.googleapis.com/calendar/v3/calendars/primary/events',
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(event)
          }
        );

        if (response.ok) {
          results.push({ success: true, event: await response.json() });
        } else {
          results.push({ success: false, error: await response.text() });
        }
      }

      return results;
    } catch (error) {
      console.error('Error adding to calendar:', error);
      throw error;
    }
  }
}

const authManager = new AuthManager();
