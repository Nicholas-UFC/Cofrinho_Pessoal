// Blocklist de versões de pacotes com comprometimento confirmado.
// Para liberar uma versão, remova-a daqui explicitamente.
const VERSOES_BLOQUEADAS = [
  { pacote: "axios", versao: "1.14.1" },
  { pacote: "axios", versao: "0.30.4" },
];

const fs = require("fs");
const path = require("path");

function versaoInstalada(pacote) {
  const caminho = path.resolve("node_modules", pacote, "package.json");
  if (!fs.existsSync(caminho)) return null;
  return JSON.parse(fs.readFileSync(caminho, "utf8")).version;
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
