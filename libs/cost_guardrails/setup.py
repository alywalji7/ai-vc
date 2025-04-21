from setuptools import setup, find_packages

setup(
    name="cost_guardrails",
    version="0.1.0",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "fastapi>=0.109.0",
        "requests>=2.31.0",
        "numpy>=1.24.0"
    ],
    description="Cost guardrails for AI services",
    author="AI.VC Team",
    author_email="team@ai.vc",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)