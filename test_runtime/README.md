# Runtime test suite

## Instructions

0. Create a `.env` file from the `.env_template` file (copy and modify it, should never commit to Git) and source it
1. Run each individual test/file with pytest invoked as a Python module (important so the root dir is in path and `flaskr` can be imported):
    - See pytest usage in https://docs.pytest.org/en/latest/how-to/usage.html
    - `python -m pytest tests/test_mod.py::test_func[x1,y2]`
    - E.g.:
        - `python -m pytest test_runtime/test_00_register_user.py::test_register_user`
        - `python -m pytest test_runtime/test_01_login_and_upload_session.py`
        - `python -m pytest test_runtime/test_01_login_and_upload_session.py::test_login_and_upload_session[4mb_file]`

