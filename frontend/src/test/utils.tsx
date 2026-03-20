import { type ReactNode } from "react";
import { render, type RenderResult } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";

export function renderWithProviders(
    ui: ReactNode,
    { initialEntries = ["/"] }: { initialEntries?: string[] } = {},
): RenderResult {
    return render(
        <MemoryRouter initialEntries={initialEntries}>
            <AuthProvider>{ui}</AuthProvider>
        </MemoryRouter>,
    );
}
