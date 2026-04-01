import axios, {
    type AxiosInstance,
    type InternalAxiosRequestConfig,
    type AxiosResponse,
    type AxiosError,
} from "axios";

const BASE_URL: string =
    import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// withCredentials envia e recebe cookies httpOnly automaticamente — OWASP 76.
const api: AxiosInstance = axios.create({
    baseURL: BASE_URL,
    withCredentials: true,
});

api.interceptors.response.use(
    (response: AxiosResponse): AxiosResponse => response,
    async (error: AxiosError): Promise<AxiosResponse> => {
        const original = error.config as InternalAxiosRequestConfig & {
            _retry?: boolean;
        };

        if (error.response?.status === 401 && !original._retry) {
            original._retry = true;
            try {
                // O cookie 'refresh' é enviado automaticamente pelo browser.
                await axios.post(
                    `${BASE_URL}/api/token/refresh/`,
                    {},
                    { withCredentials: true },
                );
                return await api(original);
            } catch {
                localStorage.removeItem("usuario_info");
                window.location.href = "/login";
            }
        }

        return Promise.reject(error);
    },
);

export default api;
