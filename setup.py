from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

requirements = [req for req in requirements if not req.startswith('-e') and req.strip()]

setup(
    name="Company Policy Chatbot",
    version="0.1",
    author="beniaminenahid",
    packages=find_packages(),
    install_requires=requirements,
)