const BASE_URL: string =
    import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export class ErroHttp extends Error {
    response: { data: unknown; status: number };

    constructor(status: number, data: unknown) {
        super(`Erro HTTP: ${String(status)}`);
        this.response = { data, status };
    }
}

interface OpcoesRequisicao {
    method?: string;
    body?: string;
}

// credentials: "include" envia e recebe cookies httpOnly automaticamente — OWASP 76.
async function tentarRefresh(): Promise<boolean> {
    const resposta = await fetch(`${BASE_URL}/api/token/refresh/`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
    });
    return resposta.ok;
}

async function requisitar(
    url: string,
    opcoes: OpcoesRequisicao = {},
    _retry = false,
): Promise<{ data: unknown }> {
    const resposta = await fetch(`${BASE_URL}${url}`, {
        method: opcoes.method,
        body: opcoes.body,
        credentials: "include",
        headers: { "Content-Type": "application/json" },
    });

    if (resposta.status === 401 && !_retry) {
        const refreshOk = await tentarRefresh();
        if (refreshOk) {
            return requisitar(url, opcoes, true);
        }
        localStorage.removeItem("usuario_info");
        window.location.href = "/login";
        return Promise.reject(new Error("Sessão expirada"));
    }

    if (!resposta.ok) {
        const corpo: unknown = await (
            resposta.json() as Promise<unknown>
        ).catch(() => null);
        return Promise.reject(new ErroHttp(resposta.status, corpo));
    }

    const data: unknown = await (resposta.json() as Promise<unknown>);
    return { data };
}

const api = {
    get: (url: string) => requisitar(url),
    post: (url: string, corpo?: unknown) =>
        requisitar(url, {
            method: "POST",
            body: JSON.stringify(corpo ?? {}),
        }),
};

export default api;
