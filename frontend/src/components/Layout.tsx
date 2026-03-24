import { useState, type JSX } from "react";
import { Outlet } from "react-router-dom";
import MenuLateral from "./MenuLateral";
import BarraTopo from "./BarraTopo";

export default function Layout(): JSX.Element {
    const [sidebarOpen, setSidebarOpen] = useState(false);

    return (
        <div className="flex h-screen overflow-hidden">
            {/* Overlay escuro no mobile quando sidebar está aberta */}
            {sidebarOpen && (
                <div
                    className="fixed inset-0 z-20 md:hidden"
                    style={{ backgroundColor: "rgba(0,0,0,0.5)" }}
                    onClick={() => {
                        setSidebarOpen(false);
                    }}
                    aria-hidden="true"
                />
            )}

            <MenuLateral
                open={sidebarOpen}
                onClose={() => {
                    setSidebarOpen(false);
                }}
            />

            <div className="flex flex-col flex-1 overflow-hidden">
                <BarraTopo
                    onMenuClick={() => {
                        setSidebarOpen((prev) => !prev);
                    }}
                />
                <main
                    style={{ backgroundColor: "#1a1a2e" }}
                    className="flex-1 overflow-y-auto p-4 md:p-6"
                >
                    <Outlet />
                </main>
            </div>
        </div>
    );
}
