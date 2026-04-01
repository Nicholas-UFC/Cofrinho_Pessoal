import { ErroHttp } from "./cliente";

const BASE_URL: string =
    import.meta.env.VITE_API_URL ?? "http://localhost:8000";

interface UsuarioInfo {
    username: string;
    is_staff: boolean;
}

async function verificarResposta(resposta: Response): Promise<Response> {
    if (!resposta.ok) {
        const corpo: unknown = await (
            resposta.json() as Promise<unknown>
        ).catch(() => null);
        throw new ErroHttp(resposta.status, corpo);
    }
    return resposta;
}

export async function login(
    username: string,
    password: string,
): Promise<UsuarioInfo> {
    // Backend define cookies httpOnly; corpo retorna apenas info do usuário.
    const resposta = await fetch(`${BASE_URL}/api/token/`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });
    await verificarResposta(resposta);
    return resposta.json() as Promise<UsuarioInfo>;
}

export async function logout(): Promise<void> {
    // Backend blacklista o refresh token e limpa os cookies.
    await fetch(`${BASE_URL}/api/token/logout/`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
    });
}
