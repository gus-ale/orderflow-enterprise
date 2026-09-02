# Decisiones técnicas y trade-offs

## FastAPI

**A favor:** tipado, Pydantic, OpenAPI, async y productividad Python.  
**Costo:** para cargas CPU-bound intensivas hay que separar workers/modelos o usar servicios especializados.

## Angular

**A favor:** estructura fuerte para aplicaciones empresariales, routing, guards, forms e interceptors.  
**Costo:** mayor peso conceptual que un frontend mínimo.

## Kafka

**A favor:** durable event log, replay, consumer groups, particiones y fan-out.  
**Costo:** operación, esquemas, idempotencia, observabilidad y eventual consistency.

## gRPC

**A favor:** contratos Protobuf, eficiencia y deadlines internos.  
**Costo:** debugging menos directo que REST y exposición al browser menos natural.

## PostgreSQL por servicio

**A favor:** ownership y autonomía de dominio.  
**Costo:** joins cross-service desaparecen y las vistas globales requieren APIs/proyecciones.

## Redis

**A favor:** baja latencia para cache y estado efímero.  
**Costo:** invalidación de cache y comportamiento degradado deben diseñarse explícitamente.

## CQRS

**A favor:** read model optimizado y desacoplado.  
**Costo:** consistencia eventual y más componentes. Se usa sólo donde la lectura agregada lo justifica.

## Kubernetes

**A favor:** scheduling, self-healing, scaling y despliegues declarativos.  
**Costo:** complejidad operacional. Para una instalación chica Docker Compose puede ser suficiente.

## AWS managed services

**A favor:** reduce operación de base/Kafka/cache.  
**Costo:** costo financiero y lock-in parcial. FinOps y sizing son obligatorios antes de producción.

## IA tenant-aware y read-only

**A favor:** reduce riesgo de acciones incorrectas y mezcla de datos entre clientes.  
**Costo:** menor autonomía del agente; las escrituras futuras requieren aprobación y herramientas controladas.
