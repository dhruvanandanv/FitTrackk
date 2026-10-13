import { Api, Storage } from "./api.js";

export const Auth = {
    currentUser: null,

    async init() {
        const token = Storage.getToken();
        if (!token) {
            this.currentUser = null;
            return null;
        }

        try {
            const userWithProfile = await Api.getMe();
            this.currentUser = userWithProfile;
            Storage.setUser(userWithProfile);
            return userWithProfile;
        } catch (err) {
            console.warn("Session expired or invalid:", err.message);
            this.logout();
            return null;
        }
    },

    async register(name, email, password) {
        const res = await Api.register({ name, email, password });
        Storage.setToken(res.access_token, true);
        Storage.setUser(res.user, true);
        this.currentUser = res.user;
        return res;
    },

    async login(email, password, remember = true) {
        const res = await Api.login({ email, password });
        Storage.setToken(res.access_token, remember);
        Storage.setUser(res.user, remember);
        this.currentUser = res.user;
        return res;
    },

    async logout() {
        try {
            await Api.logout();
        } catch {
            // Ignore failure if already logged out
        } finally {
            Storage.clear();
            this.currentUser = null;
            window.location.reload();
        }
    },

    isAuthenticated() {
        return !!Storage.getToken();
    }
};
