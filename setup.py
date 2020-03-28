import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="xray_lambda_profiler",
    version="0.0.2",

    description="xray_lambda_profiler",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Mystique",
    github_repo_url="https://github.com/miztiik/xray_lambda_profiler",
    github_profile="https://github.com/miztiik",

    package_dir={"": "xray_lambda_profiler"},
    packages=setuptools.find_packages(where="xray_lambda_profiler"),

    install_requires=[
        "aws-cdk.core>=1.31.0",
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
