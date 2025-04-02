# PowerShell script to install the latest version of Python on Windows

# Check if Python is already installed
Write-Host "Checking if Python is already installed..."
$pythonCheck = python --version 2>$null
if ($pythonCheck) {
    Write-Host "Python is already installed: $pythonCheck"
    pip install -r requirements.txt
    exit
}

# Define the URL to fetch the latest Python installer
$pythonInstallerUrl = "https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe"

# Define the installer download path
$installerPath = "$env:TEMP\python_installer.exe"

# Download the installer
Write-Host "Downloading Python installer..."
Invoke-WebRequest -Uri $pythonInstallerUrl -OutFile $installerPath

# Install Python silently
Write-Host "Installing Python..."
Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait -NoNewWindow

# Verify installation
Write-Host "Verifying Python installation..."
$pythonVersion = python --version 2>$null
if ($pythonVersion) {
    Write-Host "Python successfully installed: $pythonVersion"
} else {
    Write-Host "Python installation failed."
}

# Cleanup
Remove-Item -Path $installerPath -Force
pip install -r requirements.txt
Write-Host "Installation complete."