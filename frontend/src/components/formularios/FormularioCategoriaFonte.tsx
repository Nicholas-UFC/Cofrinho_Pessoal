import { useState, type JSX } from "react";
import { inputStyle, labelStyle, INPUT_CLASS } from "./estilos";
import { SuccessMessage, ErrorMessage } from "./Mensagens";

type ActiveTab = "categoria" | "fonte";

interface FormularioCategoriaFonteProps {
    activeTab: ActiveTab;
    loading: boolean;
    success: string | null;
    error: string | null;
    onSubmit: (nome: string) => void;
}

export function FormularioCategoriaFonte({
    activeTab,
    loading,
    success,
    error,
    onSubmit,
}: FormularioCategoriaFonteProps): JSX.Element {
    const [nome, setNome] = useState("");

    function handleSubmit(e: React.SyntheticEvent): void {
        e.preventDefault();
        onSubmit(nome);
        setNome("");
    }

    const label = activeTab === "categoria" ? "Categoria" : "Fonte";
    const placeholder =
        activeTab === "categoria" ? "Ex: Alimentação" : "Ex: Nubank";

    return (
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1">
                <label
                    htmlFor="nome-simples"
                    style={labelStyle()}
                    className="text-sm"
                >
                    Nome da {label}
                </label>
                <input
                    id="nome-simples"
                    style={inputStyle()}
                    className={INPUT_CLASS}
                    value={nome}
                    onChange={(e) => {
                        setNome(e.target.value);
                    }}
                    required
                    placeholder={placeholder}
                />
            </div>
            {success && <SuccessMessage message={success} />}
            {error && <ErrorMessage message={error} />}
            <button
                type="submit"
                disabled={loading}
                style={{
                    backgroundColor: "#22c55e",
                    color: "#0f3460",
                }}
                className="rounded-lg py-2 font-semibold text-sm hover:opacity-80 disabled:opacity-50 transition-opacity"
            >
                {loading ? "Salvando..." : `Criar ${label}`}
            </button>
        </form>
    );
}
