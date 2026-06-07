$ErrorActionPreference = 'Stop'

$root = Resolve-Path (Join-Path $PSScriptRoot '..')
$toolsRoot = Join-Path $env:LOCALAPPDATA 'SeuFuturoBuildTools'
$jdkHome = Join-Path $toolsRoot 'jdk-21'
$sdkRoot = Join-Path $toolsRoot 'android-sdk'
$gradle = Join-Path $root 'android\gradlew.bat'

if (-not (Test-Path (Join-Path $jdkHome 'bin\java.exe'))) {
    throw "JDK nao encontrado em $jdkHome. Reinstale as ferramentas Android locais."
}

if (-not (Test-Path (Join-Path $sdkRoot 'platforms\android-36'))) {
    throw "Android SDK android-36 nao encontrado em $sdkRoot. Reinstale as ferramentas Android locais."
}

if (-not (Test-Path (Join-Path $root 'android\key.properties'))) {
    throw "android/key.properties nao encontrado. Crie a keystore de release antes de gerar o AAB."
}

$env:JAVA_HOME = $jdkHome
$env:ANDROID_HOME = $sdkRoot
$env:ANDROID_SDK_ROOT = $sdkRoot
$env:Path = "$jdkHome\bin;$sdkRoot\cmdline-tools\latest\bin;$sdkRoot\platform-tools;$env:Path"

Push-Location $root
try {
    & npm.cmd run build:store
    if ($LASTEXITCODE -ne 0) {
        throw "build:store terminou com codigo $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}

Push-Location (Join-Path $root 'android')
try {
    & $gradle bundleRelease
    if ($LASTEXITCODE -ne 0) {
        throw "Gradle terminou com codigo $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}
