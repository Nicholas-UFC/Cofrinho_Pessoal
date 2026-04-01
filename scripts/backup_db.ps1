# backup_db.ps1
# Faz pg_dump do banco cofrinho e salva no Google Drive.
# Projetado para rodar via Task Scheduler — se perder o horário agendado,
# roda assim que o computador ligar.
#
# Parâmetros:
#   -EnvPath      Caminho alternativo para o .env (padrão: raiz do projeto)
#   -Container    Nome do container Docker (padrão: cofrinho_db)

param(
    [string]$EnvPath   = "",
    [string]$Container = "cofrinho_db"
)

function Ler-Env {
    param([string]$Caminho)

    if (-not (Test-Path $Caminho)) {
        throw "Arquivo .env não encontrado em: $Caminho"
    }

    $resultado = @{}
    Get-Content $Caminho |
        Where-Object { $_ -match "^\s*[^#].*=.*" } |
        ForEach-Object {
            $partes = $_ -split "=", 2
            $resultado[$partes[0].Trim()] = $partes[1].Trim()
        }
    return $resultado
}

function Verificar-Container {
    param([string]$Nome)

    try {
        $status = docker inspect --format="{{.State.Running}}" $Nome 2>$null
    } catch {
        $status = $null
    }

    if ($status -ne "true") {
        throw "Container '$Nome' não está rodando. Backup cancelado."
    }
}

function Remover-BackupsAntigos {
    param([string]$Destino, [string]$Prefixo)

    Get-ChildItem -Path $Destino -Filter "${Prefixo}_*.sql" |
        Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } |
        ForEach-Object {
            Write-Host "Removendo backup antigo: $($_.Name)"
            Remove-Item $_.FullName
        }
}

function Executar-Backup {
    param(
        [string]$CaminhoEnv,
        [string]$NomeContainer
    )

    $config  = Ler-Env -Caminho $CaminhoEnv
    $usuario = $config["POSTGRES_USER"]
    $banco   = $config["POSTGRES_DB"]
    $destino = $config["BACKUP_DESTINO"]

    if (-not $usuario -or -not $banco -or -not $destino) {
        throw "POSTGRES_USER, POSTGRES_DB ou BACKUP_DESTINO não encontrados no .env."
    }

    $arquivo = "${banco}_$(Get-Date -Format 'yyyy-MM-dd').sql"
    $caminho = Join-Path $destino $arquivo

    if (-not (Test-Path $destino)) {
        New-Item -ItemType Directory -Path $destino -Force | Out-Null
    }

    Verificar-Container -Nome $NomeContainer

    Write-Host "Iniciando backup: $arquivo"
    docker exec $NomeContainer pg_dump -U $usuario $banco | Out-File -FilePath $caminho -Encoding utf8

    Write-Host "Backup salvo em: $caminho"

    Remover-BackupsAntigos -Destino $destino -Prefixo $banco

    Write-Host "Concluído."
}

# Executa apenas quando chamado diretamente (não quando dot-sourced em testes)
if ($MyInvocation.InvocationName -ne '.') {
    $ErrorActionPreference = "Stop"
    if (-not $EnvPath) {
        $EnvPath = Join-Path (Split-Path -Parent $PSScriptRoot) ".env"
    }
    try {
        Executar-Backup -CaminhoEnv $EnvPath -NomeContainer $Container
    } catch {
        Write-Error $_.Exception.Message
        exit 1
    }
}
