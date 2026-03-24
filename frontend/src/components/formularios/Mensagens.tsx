import { type JSX } from "react";

export function SuccessMessage({ message }: { message: string }): JSX.Element {
    return (
        <p style={{ color: "#22c55e" }} className="text-sm text-center mt-2">
            {message}
        </p>
    );
}

export function ErrorMessage({ message }: { message: string }): JSX.Element {
    return <p className="text-red-400 text-sm text-center mt-2">{message}</p>;
}
