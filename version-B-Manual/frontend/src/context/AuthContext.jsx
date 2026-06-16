// Holds the logged-in state for the whole app. Components read `token` to decide
// what to render and call `login` / `logout` to change it.
import { createContext, useContext, useState } from "react";
import { api, clearToken, getToken, setToken } from "../api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setTokenState] = useState(getToken());

  async function login(email, password) {
    const { access_token } = await api.login(email, password);
    setToken(access_token);
    setTokenState(access_token);
  }

  async function register(email, password) {
    await api.register(email, password);
    await login(email, password);
  }

  function logout() {
    clearToken();
    setTokenState(null);
  }

  return (
    <AuthContext.Provider value={{ token, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
