# Publicar OrderFlow en GitHub

## 1. Preparar el repositorio

Ejecutá:

```bat
PREPARE_GITHUB.bat
```

El script limpia artefactos locales y busca patrones de secretos de alto riesgo. No reemplaza una revisión manual.

## 2. Revisar antes de publicar

No deben entrar al repositorio:

- `.env` reales;
- claves AWS;
- `terraform.tfstate`;
- kubeconfig;
- private keys/certificados privados;
- API keys;
- tokens GitHub;
- contraseñas reales de clientes.

Las credenciales `admin / Admin123!` son datos **demo** documentados y no deben reutilizarse fuera del entorno local.

## 3. Inicializar Git

```bash
git init
git add .
git status
git commit -m "feat: publish OrderFlow Enterprise portfolio"
```

Creá un repositorio vacío en GitHub y luego:

```bash
git branch -M main
git remote add origin <URL_DEL_REPOSITORIO>
git push -u origin main
```

## 4. Descripción sugerida

> Distributed SaaS platform built with Angular, FastAPI, gRPC, Kafka, PostgreSQL, Redis, CQRS, Kubernetes, GitOps, AWS, SRE and tenant-aware AI.

## 5. Topics sugeridos

```text
fastapi
angular
apache-kafka
grpc
microservices
postgresql
redis
kubernetes
keda
argocd
gitops
aws
cqrs
debezium
opentelemetry
prometheus
grafana
saas
rag
```

## 6. Qué poner en el README de GitHub

El `README.md` de Stage 19 ya está diseñado para ser la portada principal. Agregá screenshots **reales** siguiendo `SCREENSHOTS_CHECKLIST.md`.

## 7. Recomendación de historial

No hace falta fabricar 19 etapas como commits falsos. Es preferible un historial real desde el momento de publicación y commits futuros claros.
