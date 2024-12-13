# VIPV Data Crowdsourcing Server

Server for a community-sourced photovoltaic data collection project.

## Installation

1. Install Python dependencies from `requirements.txt`:
    ```bash
    python -m pip install -r requirements.txt
    ```
    Other Python versions may work too.
2. Rename `secrets/template_secrets.toml` to `secrets/secrets.toml` and mofify as needed.
3. Run the server for debugging:
    ```bash
    python -m flask --app flaskr run --host=0.0.0.0 --debug
    ```

## Other notes
- The database is stored under `instance/`.
