# backup_db.ps1
# Faz pg_dump do banco cofrinho e salva no Google Drive.
# Projetado para rodar via Task Scheduler — se perder o horário agendado,
# roda assim que o computador ligar.

$ErrorActionPreference = "Stop"

$container = "cofrinho_db"

# Lê credenciais do .env (mesmo diretório do script ou raiz do projeto)
$raiz   = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $raiz ".env"

if (-not (Test-Path $envFile)) {
    Write-Error "Arquivo .env não encontrado em: $envFile"
    exit 1
}

$env = Get-Content $envFile | Where-Object { $_ -match "^\s*[^#].*=.*" } | ForEach-Object {
    $partes = $_ -split "=", 2
    [PSCustomObject]@{ Chave = $partes[0].Trim(); Valor = $partes[1].Trim() }
}

$usuario = ($env | Where-Object { $_.Chave -eq "POSTGRES_USER" }).Valor
$banco   = ($env | Where-Object { $_.Chave -eq "POSTGRES_DB" }).Valor
$destino = ($env | Where-Object { $_.Chave -eq "BACKUP_DESTINO" }).Valor

if (-not $usuario -or -not $banco -or -not $destino) {
    Write-Error "POSTGRES_USER, POSTGRES_DB ou BACKUP_DESTINO não encontrados no .env."
    exit 1
}

$arquivo = "${banco}_$(Get-Date -Format 'yyyy-MM-dd').sql"
$caminho = Join-Path $destino $arquivo

# Garante que a pasta de destino existe
if (-not (Test-Path $destino)) {
    New-Item -ItemType Directory -Path $destino -Force | Out-Null
}

# Verifica se o container está rodando
$status = docker inspect --format="{{.State.Running}}" $container 2>$null
if ($status -ne "true") {
    Write-Error "Container '$container' não está rodando. Backup cancelado."
    exit 1
}

# Gera o backup
Write-Host "Iniciando backup: $arquivo"
docker exec $container pg_dump -U $usuario $banco | Out-File -FilePath $caminho -Encoding utf8

Write-Host "Backup salvo em: $caminho"

# Remove backups com mais de 30 dias
Get-ChildItem -Path $destino -Filter "${banco}_*.sql" |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } |
    ForEach-Object {
        Write-Host "Removendo backup antigo: $($_.Name)"
        Remove-Item $_.FullName
    }

Write-Host "Concluído."
