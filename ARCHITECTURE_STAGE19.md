# OrderFlow Enterprise — Arquitectura para Portfolio

## Vista general

```mermaid
flowchart LR
    B[Browser] --> F[Angular]
    F --> G[API Gateway]
    G --> AUTH[Auth]
    G --> TEN[Tenant]
    G --> PROD[Product]
    G --> ORD[Order]
    G --> AI[AI]
    ORD -->|gRPC| INV[Inventory]
    ORD --> K[(Kafka)]
    K --> PAY[Payment]
    K --> NOTIF[Notification]
    K --> ANA[Analytics]
    K --> RT[Realtime]
    K --> STREAM[Stream Processor]
    STREAM --> AVRO[(Avro compacted topic)]
    AVRO --> QUERY[Query / CQRS]
    RT --> F

    AUTH --> DB[(PostgreSQL)]
    TEN --> DB
    PROD --> DB
    ORD --> DB
    INV --> DB
    PAY --> DB
    QUERY --> DB
    G --> REDIS[(Redis)]

    G -.metrics.-> PROM[Prometheus]
    ORD -.traces.-> OTEL[OpenTelemetry]
    PROM --> GRAF[Grafana]
    OTEL --> TEMPO[Tempo]
```

## Principio de comunicación

- **REST**: browser → gateway y operaciones síncronas orientadas a recursos.
- **gRPC**: interacción síncrona interna de baja latencia, por ejemplo reserva de stock.
- **Kafka**: hechos de negocio asíncronos y fan-out a múltiples consumidores.
- **WebSocket**: entrega de eventos al navegador en tiempo real.

## Consistencia distribuida

```mermaid
flowchart TD
    TX[Order DB transaction] --> O[orders]
    TX --> OB[outbox_events]
    OB --> W[Outbox worker]
    W --> K[Kafka]
    K --> P[Payment]
    P --> PA{approved?}
    PA -->|sí| C[Order CONFIRMED]
    PA -->|no| X[Order CANCELLED]
    X --> R[Inventory ReleaseStock]
```

## Plataforma

```mermaid
flowchart TD
    DEV[Developer] --> GH[GitHub]
    GH --> CI[GitHub Actions]
    CI --> REG[GHCR / ECR]
    GH --> GITOPS[Git desired state]
    GITOPS --> ARGO[Argo CD]
    ARGO --> K8S[Kubernetes / EKS]
    K8S --> HPA[HPA]
    K8S --> KEDA[KEDA]
    KEDA -->|consumer lag| KAFKA[Kafka/MSK]
```

## Seguridad

Defensa por capas:

1. HTTPS/TLS en el borde.
2. JWT + refresh token + RBAC.
3. Tenant membership + `X-Tenant-ID`.
4. Validación de entrada con Pydantic.
5. secretos fuera del repositorio.
6. Network Policies.
7. mTLS opcional entre workloads.
8. auditoría y trazabilidad.
9. AI Service read-only por defecto.

## Operación

- SLI/SLO y error budget.
- Alertmanager + runbooks.
- DR con RPO/RTO definidos.
- Chaos GameDays controlados.
- Performance con k6/Locust y P50/P95/P99.
