# OrderFlow Enterprise — One-Pager

## Qué es

OrderFlow Enterprise es una plataforma SaaS de gestión de pedidos e inventario utilizada como proyecto integral para demostrar diseño y construcción de sistemas backend distribuidos modernos.

## Qué problema técnico aborda

Una operación empresarial puede requerir catálogo, stock, pedidos, pagos, analítica, notificaciones, múltiples empresas y sucursales, procesamiento en tiempo real y capacidad de escalar sin convertir todo el backend en un monolito fuertemente acoplado.

## Qué construí

- Frontend Angular.
- API Gateway y microservicios FastAPI.
- REST + gRPC + Kafka.
- PostgreSQL y Redis.
- Outbox, Saga, idempotencia, retries y DLQ.
- CQRS, Avro, Schema Registry y Debezium CDC.
- WebSocket realtime.
- JWT/RBAC y SaaS multiempresa.
- Docker, Kubernetes, KEDA y GitOps con Argo CD.
- Observabilidad con Prometheus/Grafana/OpenTelemetry.
- AWS/EKS/RDS/MSK/ElastiCache como arquitectura cloud.
- SRE, disaster recovery y Chaos Engineering.
- AI Service con forecast, reposición, anomalías, RAG y agente tenant-aware.

## Decisiones destacables

**Kafka no reemplaza REST.** REST/gRPC resuelven interacción síncrona; Kafka desacopla hechos asíncronos y permite fan-out.

**Cada servicio es dueño de sus datos.** Un microservicio no modifica directamente la base de otro.

**Outbox evita el dual-write problem.** Pedido y evento se registran en la misma transacción local antes de publicar.

**Saga evita una transacción distribuida global.** Ante un pago rechazado se compensa la reserva de stock.

**KEDA escala consumers por lag.** Kafka distribuye particiones; Kubernetes crea Pods; KEDA conecta la métrica con el escalado.

**La IA no tiene acceso irrestricto.** Es tenant-aware y read-only por defecto.

## Qué mostrar en una entrevista

1. Crear pedido.
2. Ver `orders.created` en Kafka UI.
3. Ver Payment consumir y publicar resultado.
4. Ver estado proyectado vía CQRS.
5. Ver evento realtime en Angular.
6. Mostrar métricas/trazas en Grafana.
7. Explicar Outbox/Saga y el comportamiento ante fallo.

## Estado

Proyecto preparado para portfolio y demo local. La infraestructura cloud está definida como código y requiere ejecución/validación final en una cuenta real antes de declarar producción.
