import { describe, it, expect } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "../../test/server";
import { makeFakeToken } from "../../test/handlers";
import { getResumo } from "../financas";

// ---------------------------------------------------------------------------
// Interceptor de requisição — injeção automática do token JWT
// ---------------------------------------------------------------------------

describe("Interceptor de requisição", () => {
    it("injeta o header Authorization quando há token no localStorage", async () => {
        let headerCapturado: string | null = null;
        server.use(
            http.get(
                "http://localhost:8000/api/financas/resumo/",
                ({ request }) => {
                    headerCapturado = request.headers.get("Authorization");
                    return HttpResponse.json({
                        total_entradas: "0",
                        total_gastos: "0",
                        saldo: "0",
                    });
                },
            ),
        );
        localStorage.setItem("access", "meu-token-de-acesso");
        await getResumo();
        expect(headerCapturado).toBe("Bearer meu-token-de-acesso");
    });

    it("não injeta Authorization header quando não há token", async () => {
        let headerCapturado: string | null = "placeholder";
        server.use(
            http.get(
                "http://localhost:8000/api/financas/resumo/",
                ({ request }) => {
                    headerCapturado = request.headers.get("Authorization");
                    return HttpResponse.json({
                        total_entradas: "0",
                        total_gastos: "0",
                        saldo: "0",
                    });
                },
            ),
        );
        // localStorage foi limpo pelo afterEach do setup
        await getResumo();
        expect(headerCapturado).toBeNull();
    });
});

// ---------------------------------------------------------------------------
// Interceptor de resposta — refresh automático em caso de 401
// ---------------------------------------------------------------------------

describe("Interceptor de resposta — refresh automático", () => {
    it("em caso de 401, tenta o refresh e repete a requisição original", async () => {
        const novoToken = makeFakeToken();
        localStorage.setItem("access", "token-expirado");
        localStorage.setItem("refresh", "refresh-valido");

        let chamadas = 0;
        server.use(
            http.get("http://localhost:8000/api/financas/resumo/", () => {
                chamadas++;
                if (chamadas === 1) {
                    return HttpResponse.json(
                        { detail: "Unauthorized" },
                        { status: 401 },
                    );
                }
                return HttpResponse.json({
                    total_entradas: "100",
                    total_gastos: "50",
                    saldo: "50",
                });
            }),
            http.post("http://localhost:8000/api/token/refresh/", () =>
                HttpResponse.json({ access: novoToken }),
            ),
        );

        const result = await getResumo();
        expect(chamadas).toBe(2);
        expect(result.data.saldo).toBe("50");
    });

    it("após refresh bem-sucedido, armazena o novo access token", async () => {
        const novoToken = makeFakeToken();
        localStorage.setItem("access", "token-antigo");
        localStorage.setItem("refresh", "refresh-valido");

        let chamadas = 0;
        server.use(
            http.get("http://localhost:8000/api/financas/resumo/", () => {
                chamadas++;
                if (chamadas === 1) {
                    return HttpResponse.json(
                        { detail: "Unauthorized" },
                        { status: 401 },
                    );
                }
                return HttpResponse.json({
                    total_entradas: "0",
                    total_gastos: "0",
                    saldo: "0",
                });
            }),
            http.post("http://localhost:8000/api/token/refresh/", () =>
                HttpResponse.json({ access: novoToken }),
            ),
        );

        await getResumo();
        expect(localStorage.getItem("access")).toBe(novoToken);
    });

    it("em caso de 401 sem refresh token, rejeita a promise", async () => {
        localStorage.setItem("access", "token-expirado");
        // Sem refresh token no localStorage

        server.use(
            http.get("http://localhost:8000/api/financas/resumo/", () =>
                HttpResponse.json({ detail: "Unauthorized" }, { status: 401 }),
            ),
        );

        await expect(getResumo()).rejects.toBeDefined();
    });
});
