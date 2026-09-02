param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('Install','Start','Stop','Status','Reset','Shortcuts')]
    [string]$Action
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

function Write-Title([string]$Text) {
    Write-Host ''
    Write-Host ('=' * 72) -ForegroundColor Cyan
    Write-Host ('  ' + $Text) -ForegroundColor Cyan
    Write-Host ('=' * 72) -ForegroundColor Cyan
}

function Run-DockerCompose([string[]]$ComposeArgs, [switch]$IgnoreExitCode) {
    & docker compose @ComposeArgs
    $code = $LASTEXITCODE
    if ($code -ne 0 -and -not $IgnoreExitCode) {
        throw "docker compose fallo (codigo $code): $($ComposeArgs -join ' ')"
    }
    return $code
}

function Ensure-DockerCommand {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        throw @'
Docker no esta instalado o no esta en PATH.
Ejecuta INSTALL_DOCKER_DESKTOP.bat y luego vuelve a ejecutar INSTALL_ORDERFLOW.bat.
OrderFlow One-Click no necesita Python ni Node instalados en Windows: todo corre en Docker.
'@
    }
}

function Ensure-DockerRunning {
    Ensure-DockerCommand
    & docker info *> $null
    if ($LASTEXITCODE -eq 0) { return }

    $candidates = @(
        "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe",
        "$env:LOCALAPPDATA\Docker\Docker Desktop.exe"
    )
    $desktop = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($desktop) {
        Write-Host 'Docker Desktop no esta iniciado. Intentando abrirlo...' -ForegroundColor Yellow
        Start-Process $desktop | Out-Null
    } else {
        throw 'Docker esta instalado pero el daemon no responde. Inicia Docker Desktop y vuelve a intentar.'
    }

    for ($i=0; $i -lt 90; $i++) {
        Start-Sleep -Seconds 2
        & docker info *> $null
        if ($LASTEXITCODE -eq 0) {
            Write-Host 'Docker Desktop listo.' -ForegroundColor Green
            return
        }
        if (($i % 10) -eq 0) { Write-Host 'Esperando a Docker Desktop...' }
    }
    throw 'Docker Desktop no quedo listo dentro del tiempo esperado.'
}

function Wait-Until([string]$Name, [scriptblock]$Check, [int]$TimeoutSeconds=180, [int]$DelaySeconds=3) {
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    Write-Host "Esperando: $Name ..."
    while ((Get-Date) -lt $deadline) {
        try {
            if (& $Check) {
                Write-Host "OK: $Name" -ForegroundColor Green
                return
            }
        } catch {}
        Start-Sleep -Seconds $DelaySeconds
    }
    throw "Timeout esperando $Name"
}

function Test-Http([string]$Url) {
    try {
        $r = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
        return ($r.StatusCode -ge 200 -and $r.StatusCode -lt 500)
    } catch { return $false }
}

function Start-Stack {
    Ensure-DockerRunning

    Write-Title 'OrderFlow - inicio de infraestructura base'
    Run-DockerCompose -ComposeArgs @('up','-d','postgres','redis','kafka')

    Wait-Until 'PostgreSQL' {
        & docker compose exec -T postgres pg_isready -U orderflow -d postgres *> $null
        return ($LASTEXITCODE -eq 0)
    } 180 3

    Wait-Until 'Redis' {
        $out = & docker compose exec -T redis redis-cli ping 2>$null
        return (($LASTEXITCODE -eq 0) -and (($out -join '') -match 'PONG'))
    } 120 2

    Wait-Until 'Kafka' {
        & docker compose exec -T kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9092 --list *> $null
        return ($LASTEXITCODE -eq 0)
    } 180 3

    Write-Title 'OrderFlow - servicios de plataforma'
    Run-DockerCompose -ComposeArgs @('up','-d',
        'kafka-init','schema-registry','kafka-connect','kafka-ui',
        'tempo','otel-collector','kafka-exporter','redis-exporter','postgres-exporter',
        'alertmanager','prometheus','grafana')

    Wait-Until 'Schema Registry' { Test-Http 'http://127.0.0.1:8081/subjects' } 180 3
    Wait-Until 'Kafka Connect / Debezium' { Test-Http 'http://127.0.0.1:8083/' } 180 3

    Write-Title 'OrderFlow - microservicios'
    Run-DockerCompose -ComposeArgs @('up','-d',
        'auth-service','tenant-service','inventory-service','product-service','order-service',
        'payment-service','notification-service','analytics-service','dlq-service','realtime-service',
        'stream-processor-service','query-service','ai-service','api-gateway')

    Wait-Until 'API Gateway' { Test-Http 'http://127.0.0.1:8000/health' } 240 3

    Write-Title 'OrderFlow - datos demo'
    & docker compose exec -T auth-service python seed.py
    if ($LASTEXITCODE -ne 0) { throw 'Fallo seed de auth-service' }
    & docker compose exec -T tenant-service python seed.py
    if ($LASTEXITCODE -ne 0) { throw 'Fallo seed de tenant-service' }
    & docker compose exec -T product-service python seed.py
    if ($LASTEXITCODE -ne 0) { throw 'Fallo seed de product-service' }

    Register-SchemasBestEffort
    Register-DebeziumBestEffort

    Write-Title 'OrderFlow - frontend'
    Run-DockerCompose -ComposeArgs @('up','-d','frontend')
    Wait-Until 'Angular / Nginx' { Test-Http 'http://127.0.0.1:4200/' } 180 3

    Write-Host ''
    Write-Host 'OrderFlow esta listo.' -ForegroundColor Green
    Write-Host 'Aplicacion:      http://localhost:4200'
    Write-Host 'API / Swagger:   http://localhost:8000/docs'
    Write-Host 'Kafka UI:        http://localhost:8088'
    Write-Host 'Grafana:         http://localhost:3000   (admin / admin)'
    Write-Host 'Prometheus:      http://localhost:9090'
    Write-Host 'Schema Registry: http://localhost:8081'
    Write-Host ''
    Write-Host 'Demo login: admin / Admin123!' -ForegroundColor Yellow
    Write-Host ''

    try { Start-Process 'http://localhost:4200' | Out-Null } catch {}
}

function Register-SchemasBestEffort {
    try {
        $reg='http://127.0.0.1:8081'
        $items=@(
            @{ subject='orderflow.order-state.v2-value'; type='AVRO'; path='contracts\avro\orderflow.order-state.v2.avsc' },
            @{ subject='orderflow.order-state.proto-value'; type='PROTOBUF'; path='contracts\protobuf\order_state.proto' }
        )
        foreach($item in $items) {
            $schema = Get-Content (Join-Path $Root $item.path) -Raw
            $body = @{ schemaType=$item.type; schema=$schema } | ConvertTo-Json -Compress
            Invoke-RestMethod -Uri "$reg/subjects/$($item.subject)/versions" -Method Post -ContentType 'application/vnd.schemaregistry.v1+json' -Body $body -TimeoutSec 10 | Out-Null
            $compat = @{ compatibility='BACKWARD_TRANSITIVE' } | ConvertTo-Json -Compress
            Invoke-RestMethod -Uri "$reg/config/$($item.subject)" -Method Put -ContentType 'application/vnd.schemaregistry.v1+json' -Body $compat -TimeoutSec 10 | Out-Null
        }
        Write-Host 'Schema Registry: contratos Avro/Protobuf registrados.' -ForegroundColor Green
    } catch {
        Write-Warning "No se pudieron registrar todos los schemas automaticamente: $($_.Exception.Message)"
    }
}

function Register-DebeziumBestEffort {
    try {
        $file = Join-Path $Root 'infra\debezium\orders-connector.json'
        $cfg = Get-Content $file -Raw | ConvertFrom-Json
        $body = @{ config=$cfg.config } | ConvertTo-Json -Depth 20 -Compress
        Invoke-RestMethod -Uri "http://127.0.0.1:8083/connectors/$($cfg.name)" -Method Put -ContentType 'application/json' -Body $body -TimeoutSec 15 | Out-Null
        Write-Host 'Debezium: connector de orders registrado.' -ForegroundColor Green
    } catch {
        Write-Warning "Debezium no pudo registrarse automaticamente: $($_.Exception.Message)"
    }
}

function Create-Shortcuts {
    $desktop = [Environment]::GetFolderPath('Desktop')
    $shell = New-Object -ComObject WScript.Shell
    foreach($x in @(
        @{name='OrderFlow - INICIAR.lnk'; target='START_ORDERFLOW.bat'},
        @{name='OrderFlow - DETENER.lnk'; target='STOP_ORDERFLOW.bat'},
        @{name='OrderFlow - ESTADO.lnk'; target='STATUS_ORDERFLOW.bat'}
    )) {
        $lnk = $shell.CreateShortcut((Join-Path $desktop $x.name))
        $lnk.TargetPath = Join-Path $Root $x.target
        $lnk.WorkingDirectory = $Root
        $lnk.Description = $x.name.Replace('.lnk','')
        $lnk.Save()
    }
    Write-Host 'Accesos directos creados en el Escritorio.' -ForegroundColor Green
}

function Install-Stack {
    Ensure-DockerRunning
    Write-Title 'OrderFlow One-Click - validacion'
    Run-DockerCompose -ComposeArgs @('config','--quiet')
    Write-Host 'docker-compose.yml valido.' -ForegroundColor Green

    Write-Title 'Descargando imagenes base'
    $infra=@('postgres','redis','kafka','schema-registry','kafka-connect','kafka-ui','tempo','otel-collector','kafka-exporter','redis-exporter','postgres-exporter','prometheus','alertmanager','grafana')
    foreach($svc in $infra) {
        Write-Host "Pull $svc ..."
        Run-DockerCompose -ComposeArgs @('pull',$svc)
    }

    Write-Title 'Construyendo OrderFlow'
    Run-DockerCompose -ComposeArgs @('build','--pull')
    Create-Shortcuts
    Start-Stack
}

function Stop-Stack {
    Ensure-DockerRunning
    Write-Title 'Deteniendo OrderFlow'
    Run-DockerCompose -ComposeArgs @('stop')
    Write-Host 'OrderFlow detenido. Los datos permanecen guardados en los volumenes Docker.' -ForegroundColor Green
}

function Status-Stack {
    Ensure-DockerRunning
    Write-Title 'Estado de OrderFlow'
    Run-DockerCompose -ComposeArgs @('ps')
    Write-Host ''
    foreach($u in @(
        'http://127.0.0.1:4200/',
        'http://127.0.0.1:8000/health',
        'http://127.0.0.1:8088/',
        'http://127.0.0.1:3000/'
    )) {
        $ok=Test-Http $u
        Write-Host (('{0,-42} {1}' -f $u, $(if($ok){'OK'}else{'NO RESPONDE'}))) -ForegroundColor $(if($ok){'Green'}else{'Yellow'})
    }
}

function Reset-Stack {
    Ensure-DockerRunning
    Write-Warning 'ESTO ELIMINA TODOS LOS DATOS LOCALES DE ORDERFLOW (PostgreSQL y Redis).'
    $confirm = Read-Host 'Escribe BORRAR para continuar'
    if ($confirm -ne 'BORRAR') {
        Write-Host 'Cancelado.'
        return
    }
    Run-DockerCompose -ComposeArgs @('down','-v','--remove-orphans')
    Start-Stack
}

try {
    switch($Action) {
        'Install'   { Install-Stack }
        'Start'     { Start-Stack }
        'Stop'      { Stop-Stack }
        'Status'    { Status-Stack }
        'Reset'     { Reset-Stack }
        'Shortcuts' { Create-Shortcuts }
    }
    exit 0
} catch {
    Write-Host ''
    Write-Host 'ERROR:' -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ''
    Write-Host 'Para diagnostico ejecuta STATUS_ORDERFLOW.bat o revisa: docker compose logs --tail=100' -ForegroundColor Yellow
    exit 1
}
