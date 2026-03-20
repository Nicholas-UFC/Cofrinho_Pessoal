import axios, {
    type AxiosInstance,
    type InternalAxiosRequestConfig,
    type AxiosResponse,
    type AxiosError,
} from "axios";

const BASE_URL: string =
    import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const api: AxiosInstance = axios.create({ baseURL: BASE_URL });

api.interceptors.request.use(
    (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
        const token = localStorage.getItem("access");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
);

api.interceptors.response.use(
    (response: AxiosResponse): AxiosResponse => response,
    async (error: AxiosError): Promise<AxiosResponse> => {
        const original = error.config as InternalAxiosRequestConfig & {
            _retry?: boolean;
        };

        if (error.response?.status === 401 && !original._retry) {
            original._retry = true;
            const refresh = localStorage.getItem("refresh");

            if (refresh) {
                try {
                    const response = await axios.post<{ access: string }>(
                        `${BASE_URL}/api/token/refresh/`,
                        { refresh },
                    );
                    localStorage.setItem("access", response.data.access);
                    original.headers.Authorization = `Bearer ${response.data.access}`;
                    return await api(original);
                } catch {
                    localStorage.removeItem("access");
                    localStorage.removeItem("refresh");
                    window.location.href = "/login";
                }
            }
        }

        return Promise.reject(error);
    },
);

export default api;
