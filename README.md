# Superset + Databricks Community (Unity Catalog)

Stack Docker para visualizar datos de la capa Gold (`gold.barrio_coverage`) en Apache Superset, conectando a Databricks SQL Warehouse Serverless.

## Arquitectura

```
┌─────────────────┐     ┌─────────────────┐
│   Superset      │     │   Postgres 15   │
│   (puerto 8088) │────▶│   (metadata DB) │
└────────┬────────┘     └─────────────────┘
         │
         │ Redis (cache/results)
         ▼
┌─────────────────┐
│   Redis 7       │
└─────────────────┘
         │
         │ HTTPS/Thrift (443)
         ▼
┌─────────────────────────────┐
│ Databricks SQL Warehouse    │
│ Serverless (Unity Catalog)  │
└─────────────────────────────┘
```

## Requisitos previos

- Docker + Docker Compose v2
- Databricks Community Edition con:
  - SQL Warehouse Serverless **Running**
  - Unity Catalog habilitado
  - Personal Access Token (PAT)

## Configuración inicial

### 1. Clonar y preparar entorno

```bash
cd /mnt/d/mariano/proyectos_produccion/data/gobierno_abierto

# Copiar plantilla de secrets
cp .env.example .env
```

### 2. Generar secrets locales

```bash
# SUPERSET_SECRET_KEY (42 chars base64)
openssl rand -base64 42

# POSTGRES_PASSWORD (18 chars base64)
openssl rand -base64 18

# REDIS_PASSWORD (18 chars base64)
openssl rand -base64 18
```

Editar `.env` y pegar los valores generados.

### 3. Obtener credenciales Databricks

| Variable | Dónde encontrarla |
|----------|-------------------|
| `DATABRICKS_SERVER_HOSTNAME` | SQL Warehouse → Connection details → Server Hostname |
| `DATABRICKS_HTTP_PATH` | Same → HTTP Path (`/sql/1.0/warehouses/...`) |
| `DATABRICKS_CATALOG` | Catalog Explorer → nombre exacto del catálogo Unity |
| `DATABRICKS_SCHEMA` | `gold` (capa Gold del pipeline) |
| `DATABRICKS_TOKEN` | Settings → Developer → Access tokens → Generate new token |

Completar estos valores en `.env`.

### 4. Arrancar SQL Warehouse

En Databricks UI: **SQL Warehouses** → tu warehouse Serverless → **Start** → esperar estado **"Running"** (1-2 min).

### 5. Levantar stack

```bash
docker-compose up -d --build
```

### 6. Inicializar Superset (solo primera vez)

```bash
# Crear usuario admin
docker-compose exec superset superset fab create-admin \
  --username admin --firstname Admin --lastname User \
  --email admin@local --password admin

# Migraciones e inicialización
docker-compose exec superset superset db upgrade
docker-compose exec superset superset init
```

## Acceso

- **URL**: http://localhost:8088
- **Usuario**: `admin`
- **Contraseña**: `admin`

## Configurar conexión Databricks en Superset

1. **Settings** → **Database Connections** → **+ Database**
2. Seleccionar **Databricks** (driver nativo)
3. Completar:

| Campo | Valor |
|-------|-------|
| **Host** | `${DATABRICKS_SERVER_HOSTNAME}` |
| **Port** | `443` |
| **HTTP Path** | `${DATABRICKS_HTTP_PATH}` |
| **Catalog** | `${DATABRICKS_CATALOG}` |
| **Schema** | `${DATABRICKS_SCHEMA}` |
| **Authentication** | Token → `${DATABRICKS_TOKEN}` |

4. **Test Connection** → **Connect**

## Crear Dataset y Dashboard

1. **Data** → **Datasets** → **+ Dataset**
   - Database: tu conexión Databricks
   - Schema: `gold`
   - Table: `barrio_coverage`

2. **Charts** → **+ Chart** → crear:
   - **Mapa coroplético**: `barrio_nombre` + `paradas_por_km2`
   - **Tabla ranking**: `barrio_nombre`, `cantidad_paradas`, `paradas_por_km2`, `ranking_cobertura`

3. **Dashboards** → **+ Dashboard** → agregar charts + filtros por `tipo_barrio`

## Comandos útiles

```bash
# Ver logs
docker-compose logs -f superset

# Reiniciar solo Superset
docker-compose restart superset

# Parar todo
docker-compose down

# Parar y borrar volúmenes (reset total)
docker-compose down -v

# Backup metadata Postgres
docker-compose exec db pg_dump -U superset superset > backup.sql
```

## Estructura de archivos

```
.
├── Dockerfile              # Imagen Superset 4.1.0 + drivers Databricks
├── docker-compose.yml      # Orquesta Superset + Postgres + Redis
├── requirements-local.txt  # databricks-sql-connector, databricks-sqlalchemy
├── superset_config.py      # Config: Redis cache, timezone, feature flags
├── .env.example            # Plantilla de secrets (no commitear .env)
└── README.md               # Este archivo
```

## Troubleshooting

| Problema | Solución |
|----------|----------|
| `connection refused` a Databricks | Verificar SQL Warehouse **Running**, HTTP Path correcto, PAT válido |
| `catalog not found` | Verificar `DATABRICKS_CATALOG` exacto en Catalog Explorer (case-sensitive) |
| Superset no inicia | `docker-compose logs superset` → revisar migraciones BD |
| Redis auth error | Verificar `REDIS_PASSWORD` coincide en `.env` y `superset_config.py` |

## Versiones

- **Superset**: 4.1.0 (LTS)
- **Postgres**: 15
- **Redis**: 7-alpine
- **Databricks SQL Connector**: ≥3.0.0
- **Databricks SQLAlchemy**: ≥3.0.0