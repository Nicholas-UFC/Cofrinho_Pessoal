import { useState, type JSX } from "react";
import { useNavigate, Navigate } from "react-router-dom";
import { useAutenticacao } from "../context/useAutenticacao";

export default function PaginaLogin(): JSX.Element {
    const { login, isAuthenticated } = useAutenticacao();
    const navigate = useNavigate();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    if (isAuthenticated) {
        return <Navigate to="/dashboard" replace />;
    }

    async function handleSubmit(e: React.SyntheticEvent): Promise<void> {
        e.preventDefault();
        setError(null);
        setLoading(true);
        try {
            await login(username, password);
            void navigate("/dashboard", { replace: true });
        } catch {
            setError("Credenciais inválidas. Tente novamente.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div
            style={{ backgroundColor: "#1a1a2e" }}
            className="min-h-screen flex flex-col items-center justify-center px-4"
        >
            <div className="mb-8 text-center">
                <h1
                    style={{ color: "#22c55e" }}
                    className="text-4xl font-bold mb-2"
                >
                    💰 Cofrinho Pessoal
                </h1>
                <p style={{ color: "#94a3b8" }} className="text-sm">
                    Controle suas finanças de forma simples
                </p>
            </div>

            <div
                style={{
                    backgroundColor: "#16213e",
                    border: "1px solid #1e3a5f",
                }}
                className="w-full max-w-md rounded-xl shadow-lg p-8"
            >
                <h2
                    style={{ color: "#f1f5f9" }}
                    className="text-xl font-semibold mb-6"
                >
                    Entrar na conta
                </h2>

                <form
                    onSubmit={(e) => {
                        void handleSubmit(e);
                    }}
                    className="flex flex-col gap-4"
                >
                    <div className="flex flex-col gap-1">
                        <label
                            htmlFor="username"
                            style={{ color: "#94a3b8" }}
                            className="text-sm font-medium"
                        >
                            Usuário
                        </label>
                        <input
                            id="username"
                            type="text"
                            value={username}
                            onChange={(e) => {
                                setUsername(e.target.value);
                            }}
                            required
                            style={{
                                backgroundColor: "#0f3460",
                                border: "1px solid #1e3a5f",
                                color: "#f1f5f9",
                            }}
                            className="rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-green-500"
                            placeholder="seu usuário"
                        />
                    </div>

                    <div className="flex flex-col gap-1">
                        <label
                            htmlFor="password"
                            style={{ color: "#94a3b8" }}
                            className="text-sm font-medium"
                        >
                            Senha
                        </label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => {
                                setPassword(e.target.value);
                            }}
                            required
                            style={{
                                backgroundColor: "#0f3460",
                                border: "1px solid #1e3a5f",
                                color: "#f1f5f9",
                            }}
                            className="rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-green-500"
                            placeholder="sua senha"
                        />
                    </div>

                    {error && (
                        <p className="text-red-400 text-sm text-center">
                            {error}
                        </p>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        style={{
                            backgroundColor: "#22c55e",
                            color: "#0f3460",
                        }}
                        className="mt-2 rounded-lg py-2 font-semibold text-sm hover:opacity-80 disabled:opacity-50 transition-opacity"
                    >
                        {loading ? "Entrando..." : "Entrar"}
                    </button>
                </form>
            </div>
        </div>
    );
}
