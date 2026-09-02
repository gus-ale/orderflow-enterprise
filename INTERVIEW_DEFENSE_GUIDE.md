# Cómo defender OrderFlow en una entrevista

## “¿Por qué microservicios?”

Porque el objetivo del proyecto es estudiar límites de dominio, escalado y fallos independientes. Para una aplicación pequeña elegiría un monolito modular; microservicios sólo se justifican cuando la separación aporta autonomía operativa suficiente para compensar la complejidad distribuida.

## “¿Kafka reemplaza REST?”

No. REST/gRPC son adecuados cuando el caller necesita una respuesta inmediata. Kafka es adecuado para hechos asíncronos que pueden interesar a varios consumidores y donde importa desacoplar productores y consumidores.

## “¿Por qué gRPC para stock?”

Order necesita una respuesta síncrona para saber si puede reservar stock. gRPC ofrece contrato Protobuf explícito, generación de stubs y deadlines; Kafka no sería ideal para una consulta/respuesta inmediata de ese tipo.

## “¿Qué problema resuelve Outbox?”

El dual-write problem. Si guardo `order` y luego publico Kafka, podría caer el broker entre ambas operaciones. Con Outbox, el pedido y el evento pendiente entran en la misma transacción local; un worker publica posteriormente.

## “¿Qué pasa si Kafka entrega dos veces?”

Los consumers son idempotentes y registran `event_id`. En sistemas distribuidos prefiero diseñar para at-least-once más idempotencia en lugar de asumir que nunca habrá duplicados.

## “¿Cómo resolvés una transacción distribuida?”

Con Saga y compensaciones. Si el pago es rechazado, Order pasa a CANCELLED y Inventory libera la reserva. No uso una transacción XA global.

## “¿Qué pasa si Payment Service cae?”

Los eventos permanecen en Kafka. El consumer group conserva el offset. Al recuperarse el consumer retoma el backlog. El lag permite observar la demora y KEDA puede aumentar réplicas hasta el límite útil dado por las particiones.

## “¿Más consumers siempre significa más rendimiento?”

No. Dentro de un consumer group una partición sólo puede asignarse a un consumer a la vez. Con 3 particiones, 6 consumers dejan aproximadamente 3 sin trabajo útil.

## “¿Qué diferencia hay entre HPA y KEDA?”

HPA escala por métricas como CPU/memoria o métricas custom. KEDA está orientado a event-driven autoscaling y puede reaccionar directamente a señales como Kafka consumer lag.

## “¿Por qué Redis?”

Cache, rate limiting distribuido, tokens/tickets efímeros y Pub/Sub realtime. No lo uso como reemplazo indiscriminado de PostgreSQL.

## “¿Qué es CQRS en este proyecto?”

El modelo de escritura sigue en Order Service, mientras Query Service mantiene una proyección separada optimizada para lectura. Kafka conecta ambos lados de forma eventual.

## “¿Outbox y CDC son lo mismo?”

No. Outbox modela un evento de negocio intencional. CDC/Debezium observa cambios físicos en tablas/WAL. Pueden convivir, pero transmiten semánticas distintas.

## “¿Qué harías distinto en una empresa pequeña?”

Reduciría piezas: monolito modular, PostgreSQL, quizá Redis, y agregaría Kafka/Kubernetes sólo cuando haya un problema real de escala, desacoplamiento o operación que lo justifique.

## “¿Qué parte está realmente probada?”

La suite automática valida lógica, contratos y configuración. La demo local requiere Docker. Kubernetes/AWS necesitan ejecutarse en la infraestructura destino para medir comportamiento real y cerrar el readiness de producción.
