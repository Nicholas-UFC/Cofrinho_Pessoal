import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import TopBar from "./TopBar";
import type { JSX } from "react";

export default function Layout(): JSX.Element {
    return (
        <div className="flex h-screen overflow-hidden">
            <Sidebar />
            <div className="flex flex-col flex-1 overflow-hidden">
                <TopBar />
                <main
                    style={{ backgroundColor: "#1a1a2e" }}
                    className="flex-1 overflow-y-auto p-6"
                >
                    <Outlet />
                </main>
            </div>
        </div>
    );
}
