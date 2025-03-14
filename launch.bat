@echo off
REM Singularity Launcher
REM Launch script for the Singularity Launcher application on Windows

REM Set version
set VERSION=0.1.0
echo Starting Singularity Launcher v%VERSION%...

REM Check for Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python not found. Please install Python 3.8 or higher.
    exit /b 1
)

REM Check for required Python packages
echo Checking dependencies...
python -c "import streamlit" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing required packages...
    REM Try to install required packages, but continue even if some fail
    python -m pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo Warning: Some packages may not have installed correctly. Continuing anyway...
    )
    
    REM Check if streamlit was installed
    python -c "import streamlit" >nul 2>nul
    if %ERRORLEVEL% neq 0 (
        echo Error: Failed to install streamlit, which is required.
        echo Please install it manually with: python -m pip install streamlit
        exit /b 1
    )
)

REM Create data directory if it doesn't exist
if not exist "data" mkdir data

REM Check for container engine
where podman >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set CONTAINER_ENGINE=podman
    echo Using Podman as container engine
    
    REM Create the singularity_net network if it doesn't exist
    podman network ls | findstr "singularity_net" >nul
    if %ERRORLEVEL% neq 0 (
        echo Creating singularity_net network...
        podman network create singularity_net
    )
) else (
    where docker >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        set CONTAINER_ENGINE=docker
        echo Using Docker as container engine
        
        REM Create the singularity_net network if it doesn't exist
        docker network ls | findstr "singularity_net" >nul
        if %ERRORLEVEL% neq 0 (
            echo Creating singularity_net network...
            docker network create singularity_net
        )
    ) else (
        set CONTAINER_ENGINE=none
        echo Warning: No container engine found. Container functionality will be limited.
    )
)

REM Create config.ini if it doesn't exist
if not exist "cfg\config.ini" (
    echo Creating config.ini from sample...
    copy "cfg\config.sample.ini" "cfg\config.ini" >nul
    
    REM Update container engine in config
    if not "%CONTAINER_ENGINE%"=="none" (
        powershell -Command "(Get-Content cfg\config.ini) -replace 'container_engine = .*', 'container_engine = %CONTAINER_ENGINE%' | Set-Content cfg\config.ini"
    )
)

REM Launch the application
echo Launching Singularity Launcher...
python -m streamlit run main.py %*
