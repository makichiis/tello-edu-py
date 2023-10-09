from setuptools import setup, find_packages

setup(
    name='tello-edu-protocol', # to change, just for testing
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'asyncio',  # asynchronous stuff
        'av'        # video streaming
    ]
)
