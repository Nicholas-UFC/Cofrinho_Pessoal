#Requires -Modules @{ ModuleName = "Pester"; ModuleVersion = "5.0.0" }
# backup_db.Tests.ps1

BeforeAll {
    $script:caminho_script = Join-Path $PSScriptRoot "backup_db.ps1"

    # Dot-source expõe as funções sem executar o bloco principal
    . $script:caminho_script
}

Describe "Ler-Env" {

    It "retorna os valores corretos do .env" {
        $envTemp = Join-Path $TestDrive ".env"
        Set-Content $envTemp "POSTGRES_USER=fulano`nPOSTGRES_DB=meudb`nBACKUP_DESTINO=C:\backup"

        $config = Ler-Env -Caminho $envTemp

        $config["POSTGRES_USER"]  | Should -Be "fulano"
        $config["POSTGRES_DB"]    | Should -Be "meudb"
        $config["BACKUP_DESTINO"] | Should -Be "C:\backup"
    }

    It "ignora linhas comentadas" {
        $envTemp = Join-Path $TestDrive ".env_comentado"
        Set-Content $envTemp "# comentario`nPOSTGRES_USER=fulano"

        $config = Ler-Env -Caminho $envTemp

        $config.Keys      | Should -Not -Contain "# comentario"
        $config["POSTGRES_USER"] | Should -Be "fulano"
    }

    It "encerra com erro se o arquivo não existe" {
        { Ler-Env -Caminho "C:\nao\existe\.env" } | Should -Throw
    }
}

Describe "Remover-BackupsAntigos" {

    It "remove arquivos com mais de 30 dias" {
        $destino = Join-Path $TestDrive "backups_antigos"
        New-Item -ItemType Directory -Path $destino -Force | Out-Null

        $arquivoAntigo = Join-Path $destino "banco_2020-01-01.sql"
        Set-Content $arquivoAntigo "dump antigo"
        (Get-Item $arquivoAntigo).LastWriteTime = (Get-Date).AddDays(-31)

        Remover-BackupsAntigos -Destino $destino -Prefixo "banco"

        Test-Path $arquivoAntigo | Should -Be $false
    }

    It "mantém arquivos com menos de 30 dias" {
        $destino = Join-Path $TestDrive "backups_recentes"
        New-Item -ItemType Directory -Path $destino -Force | Out-Null

        $arquivoRecente = Join-Path $destino "banco_2099-01-01.sql"
        Set-Content $arquivoRecente "dump recente"

        Remover-BackupsAntigos -Destino $destino -Prefixo "banco"

        Test-Path $arquivoRecente | Should -Be $true
    }

    It "não falha se não houver arquivos" {
        $destino = Join-Path $TestDrive "backups_vazios"
        New-Item -ItemType Directory -Path $destino -Force | Out-Null

        { Remover-BackupsAntigos -Destino $destino -Prefixo "banco" } | Should -Not -Throw
    }
}

Describe "backup_db.ps1 (integração)" {

    It "encerra com erro se o .env não existir" {
        $resultado = powershell -ExecutionPolicy Bypass -Command "
            & '$($script:caminho_script)' -EnvPath 'C:\nao\existe\.env'
        " 2>&1 | Out-String
        $resultado | Should -Match "Arquivo \.env"
    }

    It "encerra com erro se faltar variável no .env" {
        $envSemDestino = Join-Path $TestDrive ".env_sem_destino"
        Set-Content $envSemDestino "POSTGRES_USER=u`nPOSTGRES_DB=d"

        $resultado = powershell -ExecutionPolicy Bypass -Command "
            & '$($script:caminho_script)' -EnvPath '$envSemDestino'
        " 2>&1 | Out-String
        $resultado | Should -Match "encontrados no"
    }

    It "encerra com erro se o container não estiver rodando" {
        $envTemp     = Join-Path $TestDrive ".env_container"
        $destinoTemp = Join-Path $TestDrive "backup_container"
        New-Item -ItemType Directory -Path $destinoTemp -Force | Out-Null
        Set-Content $envTemp "POSTGRES_USER=u`nPOSTGRES_DB=d`nBACKUP_DESTINO=$destinoTemp"

        $resultado = powershell -ExecutionPolicy Bypass -Command "
            & '$($script:caminho_script)' -EnvPath '$envTemp' -Container 'container-inexistente-xyz'
        " 2>&1 | Out-String
        $resultado | Should -Match "Backup cancelado"
    }
}
