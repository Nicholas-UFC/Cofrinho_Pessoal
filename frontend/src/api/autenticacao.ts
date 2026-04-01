import axios from "axios";

const BASE_URL: string =
    import.meta.env.VITE_API_URL ?? "http://localhost:8000";

interface UsuarioInfo {
    username: string;
    is_staff: boolean;
}

export async function login(
    username: string,
    password: string,
): Promise<UsuarioInfo> {
    // Backend define cookies httpOnly; corpo retorna apenas info do usuário.
    const response = await axios.post<UsuarioInfo>(
        `${BASE_URL}/api/token/`,
        { username, password },
        { withCredentials: true },
    );
    return response.data;
}

export async function logout(): Promise<void> {
    // Backend blacklista o refresh token e limpa os cookies.
    await axios.post(
        `${BASE_URL}/api/token/logout/`,
        {},
        { withCredentials: true },
    );
}
