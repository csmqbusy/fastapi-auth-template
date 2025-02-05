### Info
This is a version of the FastAPI application template (https://github.com/csmqbusy/fastapi-template)
with the implemented functionality of authentication using cookies and JWT (JSON Web Tokens).

### Usage

1. Clone project.
2. Install the uv package manager if it is not already installed 
   (https://docs.astral.sh/uv/getting-started/installation/).
3. Apply the `uv sync` command to install dependencies.
4. Rename `.env.dev.example` to `env.dev`
5. mkdir `certs` in the root folder.
6. Generate two pairs of secret keys (RSA256) in `certs` folder: `access_private.pem`, `access_public.pem`, `refresh_private.pem`, `refresh_public.pem`

### Optional

To start the tests, you must run the docker-container (`docker compose up -d`) and create a database in it with the `example_db_test` name by default.