# Proyecto: Smart Invoice Generator

## Idea

Agente que genera facturas automáticamente a partir de una conversación natural, las envía por PayPal y hace seguimiento de pagos.

## Alcance

- Input: conversación natural (chat) describiendo servicios/productos y montos
- Generación automática de factura (PDF) con detalles, montos, impuestos
- Envío de factura al cliente por email
- Pago directo via PayPal (link de pago en la factura)
- Seguimiento de estado de pago (pendiente/pagado/vencido)
- Recordatorios automáticos de pago
- Dashboard con historial de facturas y métricas

## Tech Stack

- PayPal REST API (invoicing, payments)
- LLM (OpenAI/Anthropic) para extracción de datos de la conversación
- PDF generation (reportlab/weasyprint)
- Backend: FastAPI o Node.js
- Frontend: React o simple HTML
- DB: SQLite/PostgreSQL para historial

## Features principales

1. Chat interface para describir la factura
2. Extracción de datos con LLM (cliente, items, montos, impuestos)
3. Generación de factura PDF
4. Envío por email con link de pago PayPal
5. Tracking de estado de pago
6. Recordatorios automáticos
7. Dashboard de métricas (total facturado, pendiente, cobrado)

## Demo (3 min)

1. Conversación natural: "Factura a Juan por 5 horas de consultoría a $50/hora"
2. Sistema genera factura PDF automáticamente
3. Envía al cliente con link de pago
4. Cliente paga via PayPal
5. Dashboard muestra estado actualizado

## Criterios de evaluación (PayPal AI)

- ¿Hace un caso creíble para resolver un problema real?
- ¿El video demuestra el proyecto funcionando end-to-end?
- ¿El pitch comunica qué problema se resuelve, para quién y por qué importa?
- ¿La presentación es fácil de seguir?

## Requisitos cumplidos

- ✅ Usa PayPal (invoicing + payments)
- ✅ Usa AI (LLM para extracción de datos)
- ✅ Prototipo funcional
- ✅ Demo funcional (instrucciones de run en repo)
- ✅ Repo público con licencia
- ✅ Video demo sin trademarks de terceros
