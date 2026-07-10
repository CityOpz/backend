# CityOps Backend

CityOps Backend is the server-side application for the CityOps platform, a web system designed to let citizens report urban infrastructure issues such as damaged roads, public lighting failures, damaged public furniture, and other city-related incidents.

The backend is built with Django, Django REST Framework, PostgreSQL/PostGIS, JWT authentication, Docker, and automated quality checks through GitHub Actions and SonarCloud.

## Main Features

- User registration and authentication with JWT.
- Role-based access for citizens and administrators.
- Urban issue report creation.
- Report status management.
- Report status history tracking.
- Geospatial report location support using PostGIS.
- Image upload support through object storage.
- API documentation with Swagger/OpenAPI.
- Automated tests with PyTest.
- Code coverage reporting with pytest-cov.
- CI pipeline with GitHub Actions.
- Code quality analysis with SonarCloud.

## Tech Stack

- Python 3.12
- Django
- Django REST Framework
- PostgreSQL / PostGIS
- Simple JWT
- drf-spectacular
- Docker
- GitHub Actions
- SonarCloud
- PyTest
- Gunicorn

## Project Structure

```text
backend/
├── apps/
│   ├── reports/
│   │   ├── api/
│   │   ├── migrations/
│   │   ├── tests/
│   │   └── models.py
│   └── users/
│       ├── api/
│       ├── management/
│       ├── migrations/
│       ├── tests/
│       └── models.py
├── cityops/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── pytest.ini
├── requirements.txt
├── sonar-project.properties
└── start.sh
```

## Environment Variables

Create a `.env` file in the project root before running the application locally.

Example:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=postgresql://user:password@host:5432/database

DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_EMAIL=admin@example.com
DEFAULT_ADMIN_PASSWORD=change-this-password
DEFAULT_ADMIN_ROLE=ADMIN

AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=your-region
```

For production, set `DEBUG=False` and configure the correct domain in `ALLOWED_HOSTS`.

## How to Run

### Option 1: Run with Docker Compose

This is the recommended way to run the backend locally because the project depends on PostgreSQL/PostGIS and geospatial libraries.

1. Clone the repository:

```bash
git clone <repository-url>
cd backend
```

2. Create the `.env` file:

```bash
cp .env.example .env
```

If `.env.example` does not exist, create `.env` manually using the variables shown in the previous section.

3. Build and start the containers:

```bash
docker compose up --build
```

4. Apply database migrations if they are not already executed by the startup script:

```bash
docker compose run --rm web python manage.py migrate
```

5. Create or seed the default admin user:

```bash
docker compose run --rm web python manage.py seed_admin
```

6. Open the API in the browser:

```text
http://localhost:8000/
```

### Option 2: Run locally without Docker

This option requires PostgreSQL/PostGIS, GDAL, and other geospatial dependencies to be installed in your local environment.

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables in `.env`.

4. Apply migrations:

```bash
python manage.py migrate
```

5. Seed the admin user:

```bash
python manage.py seed_admin
```

6. Start the development server:

```bash
python manage.py runserver
```

The API will be available at:

```text
http://localhost:8000/
```

## API Documentation

The project uses `drf-spectacular` to generate OpenAPI documentation.

Common documentation routes:

```text
/api/schema/
/api/docs/
/api/swagger/
```

The exact route may depend on the current URL configuration.

Swagger allows developers to inspect available endpoints, request bodies, response schemas, and authentication requirements.

## Authentication

The backend uses JWT authentication.

A typical authentication flow is:

1. Register a user.
2. Log in with valid credentials.
3. Receive access and refresh tokens.
4. Send authenticated requests using the access token.

Example header:

```http
Authorization: Bearer <access_token>
```

## Testing

The project uses PyTest and pytest-cov.

Run tests with coverage:

```bash
docker compose run --rm web pytest --cov=apps --cov-report=xml --cov-report=term-missing
```

If running locally without Docker:

```bash
pytest --cov=apps --cov-report=xml --cov-report=term-missing
```

The coverage report is generated in:

```text
coverage.xml
```

This file is used by SonarCloud to display code coverage metrics.

## Code Quality

The repository is configured to work with SonarCloud.

SonarCloud is used to analyze:

- Code coverage
- Code duplication
- Cyclomatic complexity
- Technical debt
- Code smells
- Security issues
- Maintainability
- Reliability

The project configuration is defined in:

```text
sonar-project.properties
```

## Continuous Integration

The project uses GitHub Actions to run the CI pipeline.

The pipeline is responsible for:

- Checking out the repository.
- Building the Docker environment.
- Starting the database service.
- Running automated tests.
- Generating code coverage.
- Running the SonarCloud scan.

The CI workflow is located in:

```text
.github/workflows/
```

## Deployment

The backend is prepared to run as a Dockerized web service.

In production, the container starts the application using `start.sh`, which typically performs the following tasks:

```bash
python manage.py migrate
python manage.py seed_admin
gunicorn cityops.wsgi:application --bind 0.0.0.0:${PORT:-10000}
```

For deployment platforms such as Render, configure the required environment variables in the platform dashboard and make sure the service exposes the expected port.

## Database

The backend uses PostgreSQL with PostGIS support.

PostGIS is required because reports include geospatial information, such as latitude and longitude coordinates.

Database schema changes are managed through Django migrations.

Create new migrations after changing models:

```bash
docker compose run --rm web python manage.py makemigrations
```

Apply migrations:

```bash
docker compose run --rm web python manage.py migrate
```

## Security Notes

- Do not commit `.env` files.
- Do not hardcode passwords or access keys.
- Use strong secrets in production.
- Run the application as a non-root user inside Docker.
- Keep dependencies updated and pinned.
- Use HTTPS in production.
- Configure `DEBUG=False` in production.

## Contributors

```text
- Keyner Meneses Recuero 
- Juan Carlos Toro Cifuentes
- Reinel Fabian Vargas
- Felipe García 
- Mateo Noguera Pinto
```

## License

This project is intended for academic purposes. Update this section if a formal license is added.
