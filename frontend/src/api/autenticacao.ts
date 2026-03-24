import axios from "axios";

const BASE_URL: string =
    import.meta.env.VITE_API_URL ?? "http://localhost:8000";

interface TokenResponse {
    access: string;
    refresh: string;
}

export async function login(
    username: string,
    password: string,
): Promise<TokenResponse> {
    const response = await axios.post<TokenResponse>(
        `${BASE_URL}/api/token/`,
        {
            username,
            password,
        },
    );
    return response.data;
}
