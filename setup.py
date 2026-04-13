from setuptools import setup, find_packages

setup(
    name="blockconvey-monitor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["httpx>=0.24.0"],
    extras_require={
        "langchain": ["langchain-core>=0.1.0"],
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.20.0"],
        "bedrock": ["boto3>=1.26.0"],
        "litellm": ["litellm>=1.0.0"],
        "all": ["langchain-core>=0.1.0", "openai>=1.0.0", "anthropic>=0.20.0", "boto3>=1.26.0", "litellm>=1.0.0"],
    },
    python_requires=">=3.8",
    author="Block Convey",
    author_email="arunprasad@blockconvey.com",
    description="Production AI agent observability for regulated industries",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Block-Convey/blockconvey-monitor",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
