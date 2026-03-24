import { type ReactNode } from "react";
import { render, type RenderResult } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { ProvedorAutenticacao } from "../context/ContextoAutenticacao";

export function renderWithProviders(
    ui: ReactNode,
    { initialEntries = ["/"] }: { initialEntries?: string[] } = {},
): RenderResult {
    return render(
        <MemoryRouter initialEntries={initialEntries}>
            <ProvedorAutenticacao>{ui}</ProvedorAutenticacao>
        </MemoryRouter>,
    );
}
