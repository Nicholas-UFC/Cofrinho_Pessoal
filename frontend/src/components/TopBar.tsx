import { useState, useRef, useEffect, type JSX } from "react";
import { useAuth } from "../context/useAuth";

const DJANGO_ADMIN_URL: string =
    import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export default function TopBar(): JSX.Element {
    const { username, isAdmin, logout } = useAuth();
    const [open, setOpen] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        function handleClickOutside(event: MouseEvent): void {
            if (
                menuRef.current &&
                !menuRef.current.contains(event.target as Node)
            ) {
                setOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    return (
        <header
            style={{
                backgroundColor: "#16213e",
                borderBottom: "1px solid #1e3a5f",
            }}
            className="flex items-center justify-between px-6 h-14 shadow"
        >
            <div
                style={{ color: "#22c55e" }}
                className="text-lg font-semibold"
            >
                💰
            </div>

            <div className="relative" ref={menuRef}>
                <button
                    onClick={() => {
                        setOpen((prev) => !prev);
                    }}
                    style={{ color: "#f1f5f9" }}
                    className="flex items-center gap-2 text-sm font-medium hover:opacity-80 transition-opacity"
                >
                    <span style={{ color: "#94a3b8" }}>Olá,</span>
                    <span style={{ color: "#22c55e" }}>{username}</span>
                    <span style={{ color: "#94a3b8" }}>▾</span>
                </button>

                {open && (
                    <div
                        style={{
                            backgroundColor: "#16213e",
                            border: "1px solid #1e3a5f",
                        }}
                        className="absolute right-0 mt-2 w-48 rounded-lg shadow-lg py-1 z-50"
                    >
                        {isAdmin && (
                            <a
                                href={`${DJANGO_ADMIN_URL}/admin/`}
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{ color: "#f1f5f9" }}
                                className="flex items-center gap-2 px-4 py-2 text-sm hover:opacity-70 transition-opacity"
                                onClick={() => {
                                    setOpen(false);
                                }}
                            >
                                <span>⚙️</span>
                                Painel Admin
                            </a>
                        )}
                        <button
                            onClick={() => {
                                setOpen(false);
                                logout();
                            }}
                            style={{ color: "#f1f5f9" }}
                            className="w-full flex items-center gap-2 px-4 py-2 text-sm hover:opacity-70 transition-opacity"
                        >
                            <span>🚪</span>
                            Logout
                        </button>
                    </div>
                )}
            </div>
        </header>
    );
}
