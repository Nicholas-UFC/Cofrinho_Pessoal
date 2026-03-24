"""Verifica se arquivos Python ultrapassam 500 linhas (Clean Code regra 7)."""

import sys
from pathlib import Path

MAX_LINES = 500
SKIP_BLANK = True
SKIP_COMMENTS = True


def contar_linhas(path: Path) -> int:
    linhas = path.read_text(encoding="utf-8").splitlines()
    if SKIP_BLANK:
        linhas = [l for l in linhas if l.strip()]
    if SKIP_COMMENTS:
        linhas = [l for l in linhas if not l.strip().startswith("#")]
    return len(linhas)


def main() -> None:
    arquivos = [Path(f) for f in sys.argv[1:] if f.endswith(".py")]
    violacoes: list[tuple[Path, int]] = []

    for arquivo in arquivos:
        total = contar_linhas(arquivo)
        if total > MAX_LINES:
            violacoes.append((arquivo, total))

    if violacoes:
        print("Clean Code regra 7 — arquivos acima de 500 linhas:")
        for arquivo, total in violacoes:
            print(f"  {arquivo}: {total} linhas (max {MAX_LINES})")
        sys.exit(1)


if __name__ == "__main__":
    main()
