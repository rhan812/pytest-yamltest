from setuptools import setup, find_packages

setup(name="pytest-yamltest",
      version="1.0.0",
      description="pytest yamltest plugins",
      author="QA",
      packages=find_packages(),
      include_package_data=True,
      py_modules=['pytest_yamltest'],
      install_requires=[
          "pytest==3.3.2",
          "allure-pytest==2.2.3b1",
          "pyyaml",
          "objectpath",
          "click",
          "colorama",
          "pytz",
          "numpy",
          "regex",
          "cryptography",
          "paramiko",
          "uiautomator2",
          "weditor",
          "pychrome"
      ],
      entry_points={"pytest11": ["pytest_yamltest = pytest_yamltest"]}

      )
