# tutorial

## Getting Started

- Change directory into your newly created project if not already there. Your
  current directory should be the same as this `README.md` file and `pyproject.toml`.

  ```
  cd tutorial
  ```

- Create a Python virtual environment, if not already created.

  ```
  python3 -m venv env
  ```

- Upgrade packaging tools, if necessary.

  ```
  env/bin/pip install --upgrade pip
  ```

- Install the project in editable mode with its testing requirements.

  ```
  env/bin/pip install -e ".[testing]"
  ```

- Run your project's tests.

  ```
  env/bin/pytest
  ```

- Run your project.

  ```
  env/bin/pserve development.ini
  ```
