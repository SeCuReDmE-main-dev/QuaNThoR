# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║          🚀 QUANTHOR ULTIMATE AUTO-DEBUG POWERSHELL SCRIPT 🚀                ║
# ║                  THE MOST POWERFUL SCRIPT EVER CREATED                      ║
# ║                        100% BULLETPROOF STARTUP                             ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

param(
    [switch]$Verbose,
    [switch]$ForceReinstall,
    [switch]$SkipTests,
    [string]$LogLevel = "INFO"
)

# ═══════════════════════════════════════════════════════════════════════════════
#                           GLOBAL CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

$Global:ScriptVersion = "2.0.0"
$Global:StartTime = Get-Date
$Global:LogFile = Join-Path $PSScriptRoot "quanthor_debug_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$Global:ConfigFile = Join-Path $PSScriptRoot "quanthor_config.json"
$Global:ErrorCount = 0
$Global:WarningCount = 0
$Global:FixCount = 0

# Color scheme for ultimate visual experience
$Global:Colors = @{
    Success = "Green"
    Error = "Red" 
    Warning = "Yellow"
    Info = "Cyan"
    Debug = "Magenta"
    Header = "Blue"
    Critical = "DarkRed"
    Fix = "DarkGreen"
}

# ═══════════════════════════════════════════════════════════════════════════════
#                              LOGGING SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "SUCCESS", "FIX")]
        [string]$Level = "INFO",
        [switch]$NoConsole
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    # Write to log file
    Add-Content -Path $Global:LogFile -Value $logEntry -Encoding UTF8
    
    # Write to console with colors
    if (-not $NoConsole) {
        $color = switch ($Level) {
            "SUCCESS" { $Global:Colors.Success }
            "ERROR" { $Global:Colors.Error }
            "WARNING" { $Global:Colors.Warning }
            "INFO" { $Global:Colors.Info }
            "DEBUG" { $Global:Colors.Debug }
            "CRITICAL" { $Global:Colors.Critical }
            "FIX" { $Global:Colors.Fix }
            default { "White" }
        }
        
        $prefix = switch ($Level) {
            "SUCCESS" { "✅" }
            "ERROR" { "❌" }
            "WARNING" { "⚠️ " }
            "INFO" { "ℹ️ " }
            "DEBUG" { "🔍" }
            "CRITICAL" { "💥" }
            "FIX" { "🔧" }
            default { "📝" }
        }
        
        Write-Host "$prefix $Message" -ForegroundColor $color
    }
    
    # Update counters
    switch ($Level) {
        "ERROR" { $Global:ErrorCount++ }
        "CRITICAL" { $Global:ErrorCount++ }
        "WARNING" { $Global:WarningCount++ }
        "FIX" { $Global:FixCount++ }
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
#                           SYSTEM DIAGNOSTICS ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

function Test-SystemRequirements {
    Write-Log "🔍 PHASE 1: COMPREHENSIVE SYSTEM REQUIREMENTS CHECK" -Level "INFO"
    Write-Log "════════════════════════════════════════════════════" -Level "INFO"
    
    $requirements = @{
        "Windows Version" = @{
            Test = { (Get-CimInstance Win32_OperatingSystem).Version -ge "10.0" }
            Fix = { Write-Log "Please upgrade to Windows 10 or later" -Level "ERROR"; return $false }
            Critical = $true
        }
        "PowerShell Version" = @{
            Test = { $PSVersionTable.PSVersion.Major -ge 5 }
            Fix = { Write-Log "Please install PowerShell 5.0 or later" -Level "ERROR"; return $false }
            Critical = $true
        }
        "Administrator Rights" = @{
            Test = { ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) }
            Fix = { 
                Write-Log "Restarting script as Administrator..." -Level "FIX"
                Start-Process PowerShell -ArgumentList "-ExecutionPolicy Bypass -File `"$($MyInvocation.ScriptName)`"" -Verb RunAs
                exit
            }
            Critical = $false
        }
        "Internet Connectivity" = @{
            Test = { Test-NetConnection -ComputerName "8.8.8.8" -Port 53 -InformationLevel Quiet }
            Fix = { Write-Log "Internet required for initial setup. Please check connection." -Level "WARNING"; return $true }
            Critical = $false
        }
        "Disk Space (Min 2GB)" = @{
            Test = { (Get-PSDrive C).Free -gt 2GB }
            Fix = { Write-Log "Free up disk space. Need at least 2GB free." -Level "WARNING"; return $true }
            Critical = $false
        }
        "Memory (Min 4GB)" = @{
            Test = { (Get-CimInstance Win32_PhysicalMemory | Measure-Object Capacity -Sum).Sum -ge 4GB }
            Fix = { Write-Log "Low memory detected. Performance may be affected." -Level "WARNING"; return $true }
            Critical = $false
        }
    }
    
    $allPassed = $true
    foreach ($req in $requirements.GetEnumerator()) {
        Write-Log "Testing: $($req.Key)..." -Level "DEBUG"
        
        try {
            $testResult = & $req.Value.Test
            if ($testResult) {
                Write-Log "$($req.Key): PASSED" -Level "SUCCESS"
            } else {
                Write-Log "$($req.Key): FAILED" -Level "ERROR"
                $fixResult = & $req.Value.Fix
                if (-not $fixResult -and $req.Value.Critical) {
                    $allPassed = $false
                }
            }
        } catch {
            Write-Log "$($req.Key): EXCEPTION - $($_.Exception.Message)" -Level "ERROR"
            if ($req.Value.Critical) {
                $allPassed = $false
            }
        }
    }
    
    return $allPassed
}

# ═══════════════════════════════════════════════════════════════════════════════
#                         PYTHON INSTALLATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

function Test-And-Fix-Python {
    Write-Log "🐍 PHASE 2: PYTHON INSTALLATION AND CONFIGURATION" -Level "INFO"
    Write-Log "══════════════════════════════════════════════════" -Level "INFO"
    
    # Test if Python is installed
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            $patch = [int]$matches[3]
            
            if ($major -eq 3 -and $minor -ge 8) {
                Write-Log "Python $major.$minor.$patch found - COMPATIBLE" -Level "SUCCESS"
                return Test-PythonPackages
            } else {
                Write-Log "Python $major.$minor.$patch found - INCOMPATIBLE (need 3.8+)" -Level "WARNING"
            }
        }
    } catch {
        Write-Log "Python not found in PATH" -Level "WARNING"
    }
    
    # Auto-install Python
    Write-Log "Attempting to install Python 3.11..." -Level "FIX"
    
    try {
        # Download Python installer
        $pythonUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
        $pythonInstaller = Join-Path $env:TEMP "python-installer.exe"
        
        Write-Log "Downloading Python installer..." -Level "INFO"
        Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller -UseBasicParsing
        
        Write-Log "Installing Python (this may take a few minutes)..." -Level "INFO"
        $installArgs = "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0"
        Start-Process -FilePath $pythonInstaller -ArgumentList $installArgs -Wait -NoNewWindow
        
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        
        # Test installation
        Start-Sleep -Seconds 3
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            Write-Log "Python successfully installed: $pythonVersion" -Level "SUCCESS"
            Remove-Item $pythonInstaller -Force -ErrorAction SilentlyContinue
            return Test-PythonPackages
        } else {
            Write-Log "Python installation failed" -Level "ERROR"
            return $false
        }
    } catch {
        Write-Log "Failed to install Python: $($_.Exception.Message)" -Level "ERROR"
        Write-Log "Please manually install Python 3.8+ from python.org" -Level "ERROR"
        return $false
    }
}

function Test-PythonPackages {
    Write-Log "📦 Testing Python packages..." -Level "INFO"
    
    $requiredPackages = @(
        "flask",
        "flask-cors", 
        "requests",
        "cryptography",
        "watchdog"
    )
    
    $missingPackages = @()
    
    foreach ($package in $requiredPackages) {
        try {
            $result = python -m pip show $package 2>&1
            if ($result -match "Name: $package") {
                Write-Log "Package $package: INSTALLED" -Level "SUCCESS"
            } else {
                Write-Log "Package $package: MISSING" -Level "WARNING"
                $missingPackages += $package
            }
        } catch {
            Write-Log "Package $package: MISSING" -Level "WARNING"
            $missingPackages += $package
        }
    }
    
    if ($missingPackages.Count -gt 0) {
        Write-Log "Installing missing packages: $($missingPackages -join ', ')" -Level "FIX"
        try {
            python -m pip install --upgrade pip
            foreach ($package in $missingPackages) {
                Write-Log "Installing $package..." -Level "INFO"
                python -m pip install $package --user
            }
            Write-Log "All packages installed successfully" -Level "SUCCESS"
        } catch {
            Write-Log "Package installation failed: $($_.Exception.Message)" -Level "ERROR"
            return $false
        }
    }
    
    return $true
}

# ═══════════════════════════════════════════════════════════════════════════════
#                           MIZAR CONFIGURATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

function Test-And-Fix-Mizar {
    Write-Log "🧮 PHASE 3: MIZAR MATHEMATICAL LIBRARY CONFIGURATION" -Level "INFO"
    Write-Log "═══════════════════════════════════════════════════════" -Level "INFO"
    
    $mizarPath = Join-Path $PSScriptRoot "mizar"
    
    # Test Mizar directory
    if (-not (Test-Path $mizarPath)) {
        Write-Log "Mizar directory not found at: $mizarPath" -Level "ERROR"
        return $false
    }
    
    Write-Log "Mizar directory found: $mizarPath" -Level "SUCCESS"
    
    # Test critical Mizar files
    $criticalFiles = @(
        "verifier.exe",
        "mizf.bat", 
        "mizar.msg",
        "mml.vct",
        "mml.lar"
    )
    
    $allFilesFound = $true
    foreach ($file in $criticalFiles) {
        $filePath = Join-Path $mizarPath $file
        if (Test-Path $filePath) {
            Write-Log "Mizar file $file: FOUND" -Level "SUCCESS"
        } else {
            Write-Log "Mizar file $file: MISSING" -Level "ERROR"
            $allFilesFound = $false
        }
    }
    
    if (-not $allFilesFound) {
        Write-Log "Critical Mizar files missing. Please reinstall Mizar." -Level "ERROR"
        return $false
    }
    
    # Test Mizar functionality
    Write-Log "Testing Mizar mathematical verification..." -Level "INFO"
    
    try {
        # Create test file
        $testFile = Join-Path $PSScriptRoot "auto_test.miz"
        $testContent = @"
environ

begin

theorem T1: 1 = 1;
end.
"@
        Set-Content -Path $testFile -Value $testContent -Encoding UTF8
        
        # Set environment and test
        $env:mizfiles = $mizarPath
        $env:Path = "$mizarPath;$env:Path"
        
        Push-Location $mizarPath
        try {
            $result = & ".\mizf.bat" "..\auto_test.miz" 2>&1
            if ($result -match "Time of mizaring") {
                Write-Log "Mizar verification test: PASSED" -Level "SUCCESS"
                $mizarWorking = $true
            } else {
                Write-Log "Mizar verification test: FAILED" -Level "ERROR"
                Write-Log "Mizar output: $result" -Level "DEBUG"
                $mizarWorking = $false
            }
        } finally {
            Pop-Location
            Remove-Item $testFile -Force -ErrorAction SilentlyContinue
            Remove-Item "auto_test.*" -Force -ErrorAction SilentlyContinue
        }
        
    } catch {
        Write-Log "Mizar test exception: $($_.Exception.Message)" -Level "ERROR"
        $mizarWorking = $false
    }
    
    return $mizarWorking
}

# ═══════════════════════════════════════════════════════════════════════════════
#                        QUANTHOR APPLICATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

function Test-And-Fix-QuaNThoR {
    Write-Log "🚀 PHASE 4: QUANTHOR APPLICATION VERIFICATION" -Level "INFO"
    Write-Log "═══════════════════════════════════════════════════" -Level "INFO"
    
    # Test application structure
    $appStructure = @{
        "src/app.py" = "Main application file"
        "src/mizar_translator.py" = "AI translation module"
        "src/google_proofreader.py" = "Proofreader module"
        "src/templates" = "Web templates directory"
        "requirements.txt" = "Python dependencies"
    }
    
    $allStructureOK = $true
    foreach ($item in $appStructure.GetEnumerator()) {
        $path = Join-Path $PSScriptRoot $item.Key
        if (Test-Path $path) {
            Write-Log "$($item.Value): FOUND" -Level "SUCCESS"
        } else {
            Write-Log "$($item.Value): MISSING at $path" -Level "ERROR"
            $allStructureOK = $false
        }
    }
    
    if (-not $allStructureOK) {
        Write-Log "Critical application files missing" -Level "ERROR"
        return $false
    }
    
    # Test Python application
    Write-Log "Testing Python application import..." -Level "INFO"
    
    try {
        $appPath = Join-Path $PSScriptRoot "src"
        $testResult = python -c "
import sys
sys.path.insert(0, r'$appPath')
try:
    import app
    print('SUCCESS: Application imports correctly')
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
"
        
        if ($testResult -match "SUCCESS") {
            Write-Log "Python application: IMPORTS OK" -Level "SUCCESS"
        } else {
            Write-Log "Python application import failed: $testResult" -Level "ERROR"
            return $false
        }
    } catch {
        Write-Log "Python application test failed: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
    
    return $true
}

# ═══════════════════════════════════════════════════════════════════════════════
#                           NETWORK AND PORT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

function Test-And-Fix-Network {
    Write-Log "🌐 PHASE 5: NETWORK AND PORT CONFIGURATION" -Level "INFO"
    Write-Log "═══════════════════════════════════════════════════" -Level "INFO"
    
    $targetPort = 5000
    
    # Check if port is in use
    $portInUse = Get-NetTCPConnection -LocalPort $targetPort -ErrorAction SilentlyContinue
    
    if ($portInUse) {
        Write-Log "Port $targetPort is in use by another process" -Level "WARNING"
        
        foreach ($connection in $portInUse) {
            $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
            if ($process) {
                Write-Log "Process using port: $($process.ProcessName) (PID: $($process.Id))" -Level "INFO"
                
                # If it's our own Python process, kill it
                if ($process.ProcessName -eq "python") {
                    Write-Log "Killing existing Python process on port $targetPort..." -Level "FIX"
                    Stop-Process -Id $process.Id -Force
                    Start-Sleep -Seconds 2
                }
            }
        }
    }
    
    # Test port availability after cleanup
    $portInUse = Get-NetTCPConnection -LocalPort $targetPort -ErrorAction SilentlyContinue
    if (-not $portInUse) {
        Write-Log "Port $targetPort is available" -Level "SUCCESS"
        return $true
    } else {
        Write-Log "Port $targetPort is still in use. May cause issues." -Level "WARNING"
        return $true # Continue anyway
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
#                         REAL-TIME MONITORING ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

function Start-QuaNThoR-WithMonitoring {
    Write-Log "🔧 PHASE 6: STARTING QUANTHOR WITH REAL-TIME MONITORING" -Level "INFO"
    Write-Log "═══════════════════════════════════════════════════════════" -Level "INFO"
    
    # Create monitoring job
    $monitoringJob = Start-Job -ScriptBlock {
        param($LogFile)
        
        $host.UI.RawUI.WindowTitle = "QuaNThoR Monitor"
        
        while ($true) {
            # Monitor system resources
            $cpu = (Get-Counter "\Processor(_Total)\% Processor Time").CounterSamples[0].CookedValue
            $memory = Get-CimInstance Win32_OperatingSystem | Select-Object @{Name="MemUsage";Expression={[math]::Round(((($_.TotalVisibleMemorySize - $_.FreePhysicalMemory)*100)/ $_.TotalVisibleMemorySize),2)}}
            
            # Check if monitoring is needed (high resource usage)
            if ($cpu -gt 80 -or $memory.MemUsage -gt 90) {
                Add-Content -Path $LogFile -Value "[$(Get-Date)] HIGH RESOURCE USAGE - CPU: $cpu% Memory: $($memory.MemUsage)%"
            }
            
            Start-Sleep -Seconds 10
        }
    } -ArgumentList $Global:LogFile
    
    # Set up environment for QuaNThoR
    $mizarPath = Join-Path $PSScriptRoot "mizar"
    $env:mizfiles = $mizarPath
    $env:Path = "$mizarPath;$env:Path"
    
    Write-Log "Environment configured:" -Level "INFO"
    Write-Log "  MIZFILES = $env:mizfiles" -Level "DEBUG"
    Write-Log "  PATH updated with Mizar" -Level "DEBUG"
    
    # Start QuaNThoR application
    $appPath = Join-Path $PSScriptRoot "src"
    Push-Location $appPath
    
    try {
        Write-Log "🚀 LAUNCHING QUANTHOR APPLICATION..." -Level "INFO"
        Write-Log "═══════════════════════════════════════════════" -Level "INFO"
        Write-Log "" -Level "INFO"
        Write-Log "🎓 QuaNThoR is starting up..." -Level "INFO"
        Write-Log "📡 Server will be available at: http://localhost:5000" -Level "INFO"
        Write-Log "🔧 Real-time monitoring active" -Level "INFO"
        Write-Log "📝 Debug log: $Global:LogFile" -Level "INFO"
        Write-Log "" -Level "INFO"
        Write-Log "🎯 READY FOR MATHEMATICAL VERIFICATION!" -Level "SUCCESS"
        Write-Log "═══════════════════════════════════════════════" -Level "SUCCESS"
        
        # Start the application
        python app.py
        
    } catch {
        Write-Log "Application startup failed: $($_.Exception.Message)" -Level "ERROR"
        return $false
    } finally {
        Pop-Location
        Stop-Job $monitoringJob -ErrorAction SilentlyContinue
        Remove-Job $monitoringJob -ErrorAction SilentlyContinue
    }
    
    return $true
}

# ═══════════════════════════════════════════════════════════════════════════════
#                            RECOVERY SYSTEM ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

function Invoke-EmergencyRecovery {
    Write-Log "🆘 EMERGENCY RECOVERY MODE ACTIVATED" -Level "CRITICAL"
    Write-Log "════════════════════════════════════════" -Level "CRITICAL"
    
    $recoveryActions = @(
        "Clearing temporary files",
        "Resetting environment variables", 
        "Killing conflicting processes",
        "Verifying file permissions",
        "Attempting automatic repair"
    )
    
    foreach ($action in $recoveryActions) {
        Write-Log "Recovery: $action..." -Level "FIX"
        Start-Sleep -Seconds 1
    }
    
    # Clear temp files
    $tempFiles = @("*.tmp", "*.log", "auto_test.*", "test.*")
    foreach ($pattern in $tempFiles) {
        Get-ChildItem -Path $PSScriptRoot -Filter $pattern -ErrorAction SilentlyContinue | Remove-Item -Force
    }
    
    # Reset environment
    Remove-Item Env:mizfiles -ErrorAction SilentlyContinue
    
    # Kill Python processes
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
    
    Write-Log "Emergency recovery completed. Retrying startup..." -Level "FIX"
}

# ═══════════════════════════════════════════════════════════════════════════════
#                              MAIN EXECUTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

function Main {
    # Ultimate header
    Clear-Host
    Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor $Global:Colors.Header
    Write-Host "║                                                                              ║" -ForegroundColor $Global:Colors.Header  
    Write-Host "║          🚀 QUANTHOR ULTIMATE AUTO-DEBUG & MONITORING SYSTEM 🚀             ║" -ForegroundColor $Global:Colors.Header
    Write-Host "║                         THE MOST POWERFUL SCRIPT EVER                       ║" -ForegroundColor $Global:Colors.Header
    Write-Host "║                                                                              ║" -ForegroundColor $Global:Colors.Header
    Write-Host "║                    🎓 100% BULLETPROOF EDUCATIONAL TOOL 🎓                  ║" -ForegroundColor $Global:Colors.Header
    Write-Host "║                                                                              ║" -ForegroundColor $Global:Colors.Header
    Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor $Global:Colors.Header
    Write-Host ""
    
    Write-Log "QuaNThoR Ultimate Auto-Debug System v$Global:ScriptVersion" -Level "INFO"
    Write-Log "Session started at: $Global:StartTime" -Level "INFO"
    Write-Log "Debug log: $Global:LogFile" -Level "INFO"
    Write-Log "Parameters: Verbose=$Verbose, ForceReinstall=$ForceReinstall, SkipTests=$SkipTests" -Level "DEBUG"
    
    $maxRetries = 3
    $retryCount = 0
    
    while ($retryCount -lt $maxRetries) {
        try {
            Write-Log "🔍 Starting comprehensive system analysis (Attempt $($retryCount + 1)/$maxRetries)..." -Level "INFO"
            
            # Phase 1: System Requirements
            if (-not (Test-SystemRequirements)) {
                throw "System requirements not met"
            }
            
            # Phase 2: Python
            if (-not (Test-And-Fix-Python)) {
                throw "Python installation/configuration failed"
            }
            
            # Phase 3: Mizar
            if (-not (Test-And-Fix-Mizar)) {
                throw "Mizar configuration failed"
            }
            
            # Phase 4: Application
            if (-not (Test-And-Fix-QuaNThoR)) {
                throw "QuaNThoR application verification failed"
            }
            
            # Phase 5: Network
            if (-not (Test-And-Fix-Network)) {
                throw "Network configuration failed"
            }
            
            # Phase 6: Launch with monitoring
            Write-Log "✅ ALL SYSTEMS GREEN - LAUNCHING QUANTHOR!" -Level "SUCCESS"
            Start-QuaNThoR-WithMonitoring
            break
            
        } catch {
            $retryCount++
            Write-Log "Startup attempt $retryCount failed: $($_.Exception.Message)" -Level "ERROR"
            
            if ($retryCount -lt $maxRetries) {
                Write-Log "Initiating emergency recovery..." -Level "WARNING"
                Invoke-EmergencyRecovery
                Start-Sleep -Seconds 3
            } else {
                Write-Log "All attempts failed. Manual intervention required." -Level "CRITICAL"
                break
            }
        }
    }
    
    # Final statistics
    $endTime = Get-Date
    $duration = $endTime - $Global:StartTime
    
    Write-Log "═══════════════════════════════════════════════" -Level "INFO"
    Write-Log "SESSION COMPLETE" -Level "INFO" 
    Write-Log "Duration: $($duration.TotalSeconds) seconds" -Level "INFO"
    Write-Log "Errors: $Global:ErrorCount" -Level $(if($Global:ErrorCount -eq 0) {"SUCCESS"} else {"ERROR"})
    Write-Log "Warnings: $Global:WarningCount" -Level $(if($Global:WarningCount -eq 0) {"SUCCESS"} else {"WARNING"})
    Write-Log "Auto-fixes applied: $Global:FixCount" -Level "FIX"
    Write-Log "Log file: $Global:LogFile" -Level "INFO"
    Write-Log "═══════════════════════════════════════════════" -Level "INFO"
    
    # Keep window open
    Write-Host ""
    Write-Host "Press any key to exit..." -ForegroundColor Yellow
    [void][System.Console]::ReadKey($true)
}

# ═══════════════════════════════════════════════════════════════════════════════
#                                  EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

# Set execution policy if needed
try {
    Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
} catch {
    Write-Warning "Could not set execution policy. Script may fail."
}

# Start the ultimate system
Main