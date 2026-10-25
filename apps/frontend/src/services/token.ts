let accessToken: string | null = null;
let onSessionExpired: (() => void) | null = null;

export const authTokenStore = {
  getToken: () => accessToken,

  setToken: (token: string | null) => {
    accessToken = token;
  },

  registerExpirationHandler: (handler: () => void) => {
    onSessionExpired = handler;

    return () => {
      if (onSessionExpired === handler) {
        onSessionExpired = null;
      }
    };
  },

  expireSession: () => {
    accessToken = null;
    onSessionExpired?.();
  },
};
