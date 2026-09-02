# Estrategia de portfolio

## Objetivo

OrderFlow debe demostrar **criterio de arquitectura**, no solamente cantidad de tecnologías.

## Orden de lectura recomendado

1. README.md.
2. RECRUITER_ONE_PAGER.md.
3. ARCHITECTURE_STAGE19.md.
4. DEMO_SCRIPT_8_MIN.md.
5. TECHNICAL_DECISIONS.md.
6. Código de `order_service`, `inventory_service`, `payment_service` y `ai_service`.

## Cuatro piezas de código para mostrar

- Transactional Outbox de Order Service.
- `inventory.proto` y llamada gRPC.
- consumer Kafka idempotente + retry/DLQ.
- AI Service con tenant propagation y política read-only.

## Mensaje central

“Puedo diseñar y construir un backend moderno de punta a punta, pero también entiendo los trade-offs y cuándo simplificar.”
