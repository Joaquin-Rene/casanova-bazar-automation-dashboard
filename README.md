# CasaNova Bazar — Automated Executive Reporting (n8n + Google Sheets + Streamlit)

Proyecto end-to-end (dataset ficticio) para automatizar reporting de un e-commerce multi-canal:
**Google Sheets → n8n (ETL + KPIs + alertas) → Google Sheets (resumen_diario) → Streamlit Dashboard**.

---

## 🧩 Problema
Emprendimientos que venden por varios canales (Instagram, WhatsApp, TiendaNube, Mercado Libre) suelen:
- registrar ventas en Excel/Sheets,
- calcular KPIs manualmente,
- no tener alertas ni un tablero ejecutivo consistente.

---

## ✅ Solución
1) **Ventas transaccionales** en `ventas_bazar` (Google Sheets).  
2) **Workflow en n8n** (PoC en trial):
- lee `ventas_bazar`,
- calcula KPIs por fecha (ventas netas, pedidos, ticket, cancelaciones, entrega, rating),
- genera alertas simples (ej. “entrega lenta”, “cancelación alta”),
- escribe la tabla agregada en `resumen_diario`.  
3) **Dashboard en Streamlit** con filtros y tabs tipo BI (Overview / Comercial / Operación / Datos).

---

## 🏗️ Arquitectura
flowchart LR
  A["Google Sheets: ventas_bazar"] --> B["n8n: Get rows"]
  B --> C["n8n: Code (JS) KPIs + alertas"]
  C --> D["Google Sheets: resumen_diario"]
  A --> E["Streamlit Dashboard"]
  D --> E

