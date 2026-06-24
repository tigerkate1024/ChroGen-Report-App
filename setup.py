from setuptools import setup, find_packages

setup(
    name="chronogene-39f-agent-ui",
    version="0.1.0",
    description="ChronoGene synthetic 39-year-old female agent and UI demo",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
)
