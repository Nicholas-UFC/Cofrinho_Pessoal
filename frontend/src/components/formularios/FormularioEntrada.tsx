import { useState, type JSX } from "react";
import { type Fonte } from "../../api/financas";
import { inputStyle, labelStyle, INPUT_CLASS } from "./estilos";
import { SuccessMessage, ErrorMessage } from "./Mensagens";

interface FormularioEntradaProps {
    fontes: Fonte[];
    loading: boolean;
    success: string | null;
    error: string | null;
    onSubmit: (
        descricao: string,
        valor: string,
        data: string,
        fonte: string,
    ) => void;
}

export function FormularioEntrada({
    fontes,
    loading,
    success,
    error,
    onSubmit,
}: FormularioEntradaProps): JSX.Element {
    const [descricao, setDescricao] = useState("");
    const [valor, setValor] = useState("");
    const [data, setData] = useState(new Date().toISOString().slice(0, 10));
    const [fonte, setFonte] = useState("");

    function handleSubmit(e: React.SyntheticEvent): void {
        e.preventDefault();
        onSubmit(descricao, valor, data, fonte);
        setDescricao("");
        setValor("");
    }

    return (
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1">
                <label
                    htmlFor="entrada-descricao"
                    style={labelStyle()}
                    className="text-sm"
                >
                    Descrição
                </label>
                <input
                    id="entrada-descricao"
                    style={inputStyle()}
                    className={INPUT_CLASS}
                    value={descricao}
                    onChange={(e) => {
                        setDescricao(e.target.value);
                    }}
                    required
                    placeholder="Ex: Salário"
                />
            </div>
            <div className="flex gap-3">
                <div className="flex flex-col gap-1 flex-1">
                    <label
                        htmlFor="entrada-valor"
                        style={labelStyle()}
                        className="text-sm"
                    >
                        Valor (R$)
                    </label>
                    <input
                        id="entrada-valor"
                        style={inputStyle()}
                        className={INPUT_CLASS}
                        type="number"
                        step="0.01"
                        min="0.01"
                        value={valor}
                        onChange={(e) => {
                            setValor(e.target.value);
                        }}
                        required
                        placeholder="0,00"
                    />
                </div>
                <div className="flex flex-col gap-1 flex-1">
                    <label
                        htmlFor="entrada-data"
                        style={labelStyle()}
                        className="text-sm"
                    >
                        Data
                    </label>
                    <input
                        id="entrada-data"
                        style={inputStyle()}
                        className={INPUT_CLASS}
                        type="date"
                        value={data}
                        onChange={(e) => {
                            setData(e.target.value);
                        }}
                        required
                    />
                </div>
            </div>
            <div className="flex flex-col gap-1">
                <label
                    htmlFor="entrada-fonte"
                    style={labelStyle()}
                    className="text-sm"
                >
                    Fonte
                </label>
                <select
                    id="entrada-fonte"
                    style={inputStyle()}
                    className={INPUT_CLASS}
                    value={fonte}
                    onChange={(e) => {
                        setFonte(e.target.value);
                    }}
                    required
                >
                    <option value="">Selecione...</option>
                    {fontes.map((f) => (
                        <option key={f.id} value={f.id}>
                            {f.nome}
                        </option>
                    ))}
                </select>
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
                {loading ? "Salvando..." : "Registrar Entrada"}
            </button>
        </form>
    );
}
