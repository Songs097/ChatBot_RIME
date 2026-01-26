from setuptools import setup, find_packages

setup(
    name='rime-chatbot',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'click',
        'requests',
        'python-dotenv',
        'rich',
    ],
    entry_points={
        'console_scripts': [
            'rime = rime.main:cli',
        ],
    },
)
