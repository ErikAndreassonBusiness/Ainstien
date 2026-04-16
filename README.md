# Ainstien

This is a Flask-based web application that uses Machine Learning to analyze company fundamental data and suggest potential trades.

---

### 🚀 Setup & Environment Management

We are using **`uv`** for this project. It is a modern, high-performance Python package manager that replaces `pip` and `venv`. We use it because it is significantly faster and ensures we are both using the exact same library versions on our Macs.

1. **Install `uv`** Run the following command in your terminal to install `uv` on your Mac:

   ```bash
   curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
   ```

2. **How the project was started (`uv init`)** For your information, this project was initialized using `uv init`. This created our `pyproject.toml` file, which acts as the blueprint for our application.

3. **Adding new libraries (`uv add`)** Whenever we need to install a new package (like `yfinance` or `plotly`), we do **not** use `pip`. Instead, use:
   ```bash
   uv add <package_name>
   ```
4. **Synchronizing your environment (`uv sync`)** After you pull new code from GitHub, run this command to make sure your local virtual environment matches the project's requirements:

   ```bash
   uv sync
   ```

5. **Activating the environment** To work within the project environment, activate it using:
   ```bash
   source .venv/bin/activate
   ```
