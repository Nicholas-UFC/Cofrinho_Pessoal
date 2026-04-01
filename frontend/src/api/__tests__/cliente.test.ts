import { describe, it, expect } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "../../test/server";
import { getResumo } from "../financas";

// ---------------------------------------------------------------------------
// Interceptor de resposta — refresh automático via cookie httpOnly
//
// O token JWT vive no cookie httpOnly (OWASP prática 76). O axios envia
// cookies automaticamente via withCredentials. Não há Authorization header
// nem armazenamento de tokens no localStorage.
// ---------------------------------------------------------------------------

describe("Interceptor de resposta — refresh automático", () => {
    it("em caso de 401, tenta o refresh e repete a requisição original", async () => {
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
                HttpResponse.json({ status: "ok" }),
            ),
        );

        const result = await getResumo();
        expect(chamadas).toBe(2);
        expect(result.data.saldo).toBe("50");
    });

    it("não injeta Authorization header — autenticação é via cookie", async () => {
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
        await getResumo();
        expect(headerCapturado).toBeNull();
    });

    it("em caso de 401 com refresh falhando, rejeita a promise", async () => {
        server.use(
            http.get("http://localhost:8000/api/financas/resumo/", () =>
                HttpResponse.json({ detail: "Unauthorized" }, { status: 401 }),
            ),
            http.post("http://localhost:8000/api/token/refresh/", () =>
                HttpResponse.json(
                    { detail: "Token inválido" },
                    { status: 401 },
                ),
            ),
        );

        await expect(getResumo()).rejects.toBeDefined();
    });
});
