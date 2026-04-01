// Blocklist de versões de pacotes com comprometimento confirmado.
// Para liberar uma versão, remova-a daqui explicitamente.
const VERSOES_BLOQUEADAS = [
  { pacote: "axios", versao: "1.14.1" },
  { pacote: "axios", versao: "0.30.4" },
];

import { readFileSync, existsSync } from "fs";
import { resolve } from "path";

function versaoInstalada(pacote) {
  const caminho = resolve("node_modules", pacote, "package.json");
  if (!existsSync(caminho)) return null;
  return JSON.parse(readFileSync(caminho, "utf8")).version;
}

let encontrou = false;

for (const { pacote, versao } of VERSOES_BLOQUEADAS) {
  const instalada = versaoInstalada(pacote);
  if (instalada === versao) {
    console.error(
      `\n[BLOQUEADO] ${pacote}@${versao} está na blocklist de pacotes comprometidos.` +
        `\nRemova ou faça downgrade antes de continuar.\n`
    );
    encontrou = true;
  }
}

if (encontrou) process.exit(1);
