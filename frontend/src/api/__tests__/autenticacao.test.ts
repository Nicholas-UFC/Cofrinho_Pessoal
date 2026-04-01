import { describe, it, expect } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "../../test/server";
import { login } from "../autenticacao";

// ---------------------------------------------------------------------------
// login — função de autenticação via JWT
// ---------------------------------------------------------------------------

describe("login", () => {
    it("retorna username e is_staff no login bem-sucedido", async () => {
        const resultado = await login("testuser", "testpass");
        expect(resultado.username).toBeTruthy();
        expect(typeof resultado.is_staff).toBe("boolean");
    });

    it("retorna username como string", async () => {
        const resultado = await login("testuser", "testpass");
        expect(typeof resultado.username).toBe("string");
    });

    it("envia username e password corretos no corpo da requisição", async () => {
        let corpoCapturado: { username?: string; password?: string } = {};
        server.use(
            http.post(
                "http://localhost:8000/api/token/",
                async ({ request }) => {
                    corpoCapturado =
                        (await request.json()) as typeof corpoCapturado;
                    return HttpResponse.json({
                        access: "token-acesso",
                        refresh: "token-refresh",
                    });
                },
            ),
        );
        await login("meususuario", "minhasenha");
        expect(corpoCapturado.username).toBe("meususuario");
        expect(corpoCapturado.password).toBe("minhasenha");
    });

    it("lança exceção com credenciais inválidas (401)", async () => {
        server.use(
            http.post("http://localhost:8000/api/token/", () =>
                HttpResponse.json(
                    { detail: "Sem conta ativa" },
                    { status: 401 },
                ),
            ),
        );
        await expect(login("errado", "errado")).rejects.toThrow();
    });

    it("lança exceção em erro de servidor (500)", async () => {
        server.use(
            http.post("http://localhost:8000/api/token/", () =>
                HttpResponse.json({ detail: "Erro interno" }, { status: 500 }),
            ),
        );
        await expect(login("user", "pass")).rejects.toThrow();
    });
});
