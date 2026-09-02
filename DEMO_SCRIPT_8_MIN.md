# Guion de Demo — 8 minutos

## 0:00–0:45 — Apertura

“OrderFlow Enterprise es una plataforma SaaS que construí para aplicar arquitectura backend moderna de punta a punta. El frontend es Angular, el backend está separado en microservicios FastAPI, uso gRPC para operaciones síncronas internas y Kafka para eventos asíncronos.”

Mostrá la pantalla principal y el README con el diagrama.

## 0:45–2:00 — Crear un pedido

1. Iniciar sesión.
2. Seleccionar empresa/tenant.
3. Crear o elegir un producto con stock.
4. Crear un pedido.

Explicación:

“Angular llama al API Gateway. El Gateway valida JWT, rol y tenant. Order Service consulta catálogo y reserva stock por gRPC en Inventory Service.”

## 2:00–3:15 — Kafka + Outbox

Abrir Kafka UI.

Mostrá `orders.created`.

“Order Service no escribe la base y Kafka como dos operaciones independientes. Utiliza Transactional Outbox para evitar el dual-write problem.”

Mostrá consumer groups y particiones si están disponibles.

## 3:15–4:15 — Saga

Mostrá un pago aprobado o utilizá el escenario de pago rechazado.

“Payment consume el pedido. Si se rechaza, publica `payments.rejected`; Order cancela y Inventory ejecuta la compensación liberando stock. No intento una transacción SQL distribuida entre servicios.”

## 4:15–5:00 — CQRS + tiempo real

Abrí la pantalla CQRS y Tiempo Real.

“Los eventos alimentan un read model independiente. El navegador recibe actualizaciones por WebSocket sin consultar repetidamente al backend.”

## 5:00–5:45 — Observabilidad

Abrí Grafana.

Mostrá requests, P95/P99, consumer lag y cualquier panel disponible.

“Además de logs tengo métricas, trazas, SLO y alertas. Para Kafka observo consumer lag, que también puede alimentar KEDA para escalado.”

## 5:45–6:45 — SaaS + IA

Cambiar de tenant si la demo tiene más de uno.

Mostrar IA Empresarial:

- forecast;
- reposición;
- anomalías;
- pregunta RAG.

“La IA hereda el tenant validado y está en read-only por defecto; no puede modificar stock ni generar pagos sin una futura aprobación explícita.”

## 6:45–7:30 — Kubernetes / GitOps / AWS

Desde documentación o terminal mostrar:

- `k8s/`
- `gitops/`
- `cloud/aws/`

“En Kubernetes uso HPA y KEDA. Git es la fuente de verdad mediante Argo CD. La arquitectura AWS separa EKS, RDS, MSK, ElastiCache, ECR y Secrets Manager.”

## 7:30–8:00 — Cierre

“Lo importante del proyecto no es la cantidad de herramientas sino por qué existe cada una: REST/gRPC para lo síncrono, Kafka para eventos, Outbox/Saga para consistencia, Redis para estado efímero/cache, CQRS para lectura y Kubernetes/KEDA para operación y escalado.”

### Regla de demo

No navegues por 40 carpetas. Mostrá **un flujo completo** y usá la arquitectura para explicar el resto.
