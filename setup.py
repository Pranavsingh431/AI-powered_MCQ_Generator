from setuptools import find_packages, setup

setup(
    name='mcqgenerator',
    version='0.0.1',
    author='Pranav Singh',
    author_email='singhpranav431@gmail.com',
    install_requires=['langchain', 'streamlit', 'python-dotenv', 'PyPDF2','transformers'],
    packages=find_packages()
)