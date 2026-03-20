import { describe, it, expect } from "vitest";
import { screen } from "@testing-library/react";
import { renderWithProviders } from "../test/utils";
import { makeFakeToken } from "../test/handlers";
import Sidebar from "./Sidebar";

describe("Sidebar — navegação", () => {
    it("exibe o link Dashboard", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<Sidebar />);
        expect(screen.getByText("Dashboard")).toBeInTheDocument();
    });

    it("exibe o link Cadastro", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<Sidebar />);
        expect(screen.getByText("Cadastro")).toBeInTheDocument();
    });

    it("exibe o link Histórico", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<Sidebar />);
        expect(screen.getByText("Histórico")).toBeInTheDocument();
    });

    it("link Dashboard aponta para /dashboard", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<Sidebar />);
        const link = screen.getByText("Dashboard").closest("a");
        expect(link?.getAttribute("href")).toBe("/dashboard");
    });

    it("link Cadastro aponta para /cadastro", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<Sidebar />);
        const link = screen.getByText("Cadastro").closest("a");
        expect(link?.getAttribute("href")).toBe("/cadastro");
    });

    it("link Histórico aponta para /historico", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<Sidebar />);
        const link = screen.getByText("Histórico").closest("a");
        expect(link?.getAttribute("href")).toBe("/historico");
    });
});

describe("Sidebar — logout", () => {
    it("exibe botão de Logout", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<Sidebar />);
        expect(screen.getByText("Logout")).toBeInTheDocument();
    });

    it("botão Logout limpa os tokens do localStorage", () => {
        localStorage.setItem("access", makeFakeToken());
        localStorage.setItem("refresh", "fake-refresh");
        renderWithProviders(<Sidebar />);
        screen.getByText("Logout").click();
        expect(localStorage.getItem("access")).toBeNull();
        expect(localStorage.getItem("refresh")).toBeNull();
    });
});
