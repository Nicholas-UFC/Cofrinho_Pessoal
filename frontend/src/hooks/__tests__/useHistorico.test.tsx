import { describe, it, expect } from "vitest";
import { renderHook, waitFor, act } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { server } from "../../test/server";
import { useHistorico } from "../useHistorico";

// ---------------------------------------------------------------------------
// useHistorico — testes do hook de histórico paginado
// ---------------------------------------------------------------------------

describe("useHistorico — carregamento", () => {
    it("busca gastos quando view é 'gastos'", async () => {
        const { result } = renderHook(() => useHistorico("gastos"));
        await waitFor(() => expect(result.current.loading).toBe(false));
        expect(result.current.gastos).not.toBeNull();
        expect(result.current.gastos?.results).toHaveLength(2);
    });

    it("busca entradas quando view é 'entradas'", async () => {
        const { result } = renderHook(() => useHistorico("entradas"));
        await waitFor(() => expect(result.current.loading).toBe(false));
        expect(result.current.entradas).not.toBeNull();
        expect(result.current.entradas?.results).toHaveLength(1);
    });

    it("gastos é null antes dos dados chegarem", () => {
        const { result } = renderHook(() => useHistorico("gastos"));
        expect(result.current.gastos).toBeNull();
    });

    it("entradas é null quando view é 'gastos'", async () => {
        const { result } = renderHook(() => useHistorico("gastos"));
        await waitFor(() => expect(result.current.loading).toBe(false));
        expect(result.current.entradas).toBeNull();
    });

    it("gastos é null quando view é 'entradas'", async () => {
        const { result } = renderHook(() => useHistorico("entradas"));
        await waitFor(() => expect(result.current.loading).toBe(false));
        expect(result.current.gastos).toBeNull();
    });

    it("error é null após busca bem-sucedida", async () => {
        const { result } = renderHook(() => useHistorico("gastos"));
        await waitFor(() => expect(result.current.loading).toBe(false));
        expect(result.current.error).toBeNull();
    });
});

describe("useHistorico — estado de erro", () => {
    it("define error quando a API de gastos retorna erro de rede", async () => {
        server.use(
            http.get("http://localhost:8000/api/financas/gastos/", () =>
                HttpResponse.error(),
            ),
        );
        const { result } = renderHook(() => useHistorico("gastos"));
        await waitFor(() =>
            expect(result.current.error).toBe("Erro ao carregar histórico."),
        );
        expect(result.current.loading).toBe(false);
    });

    it("define error quando a API de entradas retorna erro de rede", async () => {
        server.use(
            http.get("http://localhost:8000/api/financas/entradas/", () =>
                HttpResponse.error(),
            ),
        );
        const { result } = renderHook(() => useHistorico("entradas"));
        await waitFor(() =>
            expect(result.current.error).toBe("Erro ao carregar histórico."),
        );
        expect(result.current.loading).toBe(false);
    });
});

describe("useHistorico — paginação", () => {
    it("gastoPage começa em 1", () => {
        const { result } = renderHook(() => useHistorico("gastos"));
        expect(result.current.gastoPage).toBe(1);
    });

    it("entradaPage começa em 1", () => {
        const { result } = renderHook(() => useHistorico("entradas"));
        expect(result.current.entradaPage).toBe(1);
    });

    it("rebusca gastos quando gastoPage muda", async () => {
        let chamadas = 0;
        server.use(
            http.get("http://localhost:8000/api/financas/gastos/", () => {
                chamadas++;
                return HttpResponse.json({
                    count: 1,
                    next: null,
                    previous: null,
                    results: [
                        {
                            id: chamadas,
                            descricao: "G",
                            valor: "10.00",
                            data: "2026-01-01",
                            categoria: 1,
                        },
                    ],
                });
            }),
        );
        const { result } = renderHook(() => useHistorico("gastos"));
        await waitFor(() => expect(result.current.loading).toBe(false));
        expect(chamadas).toBe(1);

        act(() => {
            result.current.setGastoPage(2);
        });
        await waitFor(() => expect(chamadas).toBe(2));
    });

    it("rebusca entradas quando entradaPage muda", async () => {
        let chamadas = 0;
        server.use(
            http.get("http://localhost:8000/api/financas/entradas/", () => {
                chamadas++;
                return HttpResponse.json({
                    count: 1,
                    next: null,
                    previous: null,
                    results: [
                        {
                            id: chamadas,
                            descricao: "E",
                            valor: "50.00",
                            data: "2026-01-01",
                            fonte: 1,
                        },
                    ],
                });
            }),
        );
        const { result } = renderHook(() => useHistorico("entradas"));
        await waitFor(() => expect(result.current.loading).toBe(false));
        expect(chamadas).toBe(1);

        act(() => {
            result.current.setEntradaPage(2);
        });
        await waitFor(() => expect(chamadas).toBe(2));
    });
});
