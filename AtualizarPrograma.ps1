# Definir as pastas de origem e destino
$sourcePath = "C:\Caminho\Para\Pasta\Origem"
$destinationPath = "C:\Caminho\Para\Pasta\Destino"

# Verificar se a pasta de origem existe
if (-Not (Test-Path -Path $sourcePath)) {
    Write-Host "A pasta de origem não existe: $sourcePath"
    exit
}

# Verificar se a pasta de destino existe; caso contrário, criar a pasta
if (-Not (Test-Path -Path $destinationPath)) {
    New-Item -Path $destinationPath -ItemType Directory
}

# Copiar todos os arquivos da pasta de origem para a pasta de destino
try {
    Copy-Item -Path "$sourcePath\*" -Destination $destinationPath -Recurse -Force
    Write-Host "Arquivos copiados com sucesso de $sourcePath para $destinationPath"
} catch {
    Write-Host "Ocorreu um erro ao copiar os arquivos: $_"
}
