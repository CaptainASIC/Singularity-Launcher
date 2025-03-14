Apple:

(base) spresgraves@Samuels-MacBook-Pro Singularity-Launcher % ./launch.sh 
Starting Singularity Launcher v0.1.0...
Checking dependencies...
Installing required packages...
Collecting streamlit>=1.24.0 (from -r requirements.txt (line 1))
  Using cached streamlit-1.43.2-py2.py3-none-any.whl.metadata (8.9 kB)
Requirement already satisfied: psutil>=5.9.0 in /opt/homebrew/Caskroom/miniconda/base/lib/python3.12/site-packages (from -r requirements.txt (line 2)) (7.0.0)
Collecting py-cpuinfo>=9.0.0 (from -r requirements.txt (line 3))
  Using cached py_cpuinfo-9.0.0-py3-none-any.whl.metadata (794 bytes)
Collecting gputil>=1.4.0 (from -r requirements.txt (line 4))
  Downloading GPUtil-1.4.0.tar.gz (5.5 kB)
  Preparing metadata (setup.py) ... done
Requirement already satisfied: pyyaml>=6.0 in /opt/homebrew/Caskroom/miniconda/base/lib/python3.12/site-packages (from -r requirements.txt (line 5)) (6.0.2)
ERROR: Ignored the following yanked versions: 3.1.1.3, 3.1.2.1
ERROR: Ignored the following versions that require a different python version: 0.55.2 Requires-Python <3.5
ERROR: Could not find a version that satisfies the requirement podman-py>=4.5.0 (from versions: none)
ERROR: No matching distribution found for podman-py>=4.5.0
Error: Failed to install required packages.
(base) spresgraves@Samuels-MacBook-Pro Singularity-Launcher % 




Ubuntu x86:

(venv) (base) asic@Rocinante:~/Singularity-Launcher$ ./launch.sh
Starting Singularity Launcher v0.1.0...
Checking dependencies...
Using Podman as container engine
WARN[0000] "/" is not a shared mount, this could cause issues or missing mounts with rootless containers
Creating singularity_net network...
singularity_net
Creating config.ini from sample...
Launching Singularity Launcher...

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://172.30.59.53:8501

gio: http://localhost:8501: Operation not supported
2025-03-14 13:47:12.965 Uncaught app execution
Traceback (most recent call last):
  File "/home/asic/archon/venv/lib/python3.12/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 88, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/home/asic/archon/venv/lib/python3.12/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 579, in code_to_exec
    exec(code, module.__dict__)
  File "/home/asic/Singularity-Launcher/main.py", line 15, in <module>
    from lib.system import get_system_info, get_container_engine_info
ModuleNotFoundError: No module named 'lib'
2025-03-14 13:47:28.409 Uncaught app execution
Traceback (most recent call last):
  File "/home/asic/archon/venv/lib/python3.12/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 88, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/home/asic/archon/venv/lib/python3.12/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 579, in code_to_exec
    exec(code, module.__dict__)
  File "/home/asic/Singularity-Launcher/main.py", line 15, in <module>
    from lib.system import get_system_info, get_container_engine_info
ModuleNotFoundError: No module named 'lib'
^C  Stopping...



Windows:

G:\Repositories\Singularity-Launcher>launch.bat
Starting Singularity Launcher v0.1.0...
Checking dependencies...
Installing required packages...
Collecting streamlit>=1.24.0 (from -r requirements.txt (line 1))
  Using cached streamlit-1.43.2-py2.py3-none-any.whl.metadata (8.9 kB)
Requirement already satisfied: psutil>=5.9.0 in c:\users\asic\appdata\local\programs\python\python310\lib\site-packages (from -r requirements.txt (line 2)) (5.9.7)
Collecting py-cpuinfo>=9.0.0 (from -r requirements.txt (line 3))
  Using cached py_cpuinfo-9.0.0-py3-none-any.whl.metadata (794 bytes)
Collecting gputil>=1.4.0 (from -r requirements.txt (line 4))
  Using cached GPUtil-1.4.0.tar.gz (5.5 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Requirement already satisfied: pyyaml>=6.0 in c:\users\asic\appdata\local\programs\python\python310\lib\site-packages (from -r requirements.txt (line 5)) (6.0.1)
ERROR: Ignored the following yanked versions: 3.1.1.3, 3.1.2.1
ERROR: Ignored the following versions that require a different python version: 0.55.2 Requires-Python <3.5
ERROR: Could not find a version that satisfies the requirement podman-py>=4.5.0 (from versions: none)
ERROR: No matching distribution found for podman-py>=4.5.0

[notice] A new release of pip is available: 24.0 -> 25.0.1
[notice] To update, run: python.exe -m pip install --upgrade pip
Error: Failed to install required packages.

G:\Repositories\Singularity-Launcher>