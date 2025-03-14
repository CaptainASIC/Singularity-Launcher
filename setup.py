from setuptools import setup, find_packages

setup(
    name="singularity-launcher",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "streamlit>=1.24.0",
        "psutil>=5.9.0",
        "py-cpuinfo>=9.0.0",
        "gputil>=1.4.0",
        "pyyaml>=6.0",
        "matplotlib>=3.7.0",
        "plotly>=5.14.0",
        "pandas>=2.0.0",
        "pillow>=9.5.0",
        "requests>=2.28.0",
        "python-dotenv>=1.0.0",
        "watchdog>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "singularity-launcher=main:main",
        ],
    },
)
