// Top-level switch: no token -> Login page, otherwise the Dashboard.
import { useAuth } from "./context/AuthContext.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";

export default function App() {
  const { token } = useAuth();
  return token ? <DashboardPage /> : <LoginPage />;
}
