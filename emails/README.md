# Email marketing — Football Frenzy Shop

Generado con `python3 build.py`. Los correos están en `out/` y las vistas previas en `out/vista/`.
Las imágenes (logo y foto de cliente) ya están en Shopify > Contenido > Archivos.

## Situación (27 oct 2026)

- 11 carritos abandonados en octubre, ~$17,800 MXN. Casi todos son de 3 jerseys con 3x2.
- 7 pedidos desde el 1 de octubre.
- 368 clientes en la lista, todos suscritos a marketing.
- Una secuencia de 3 correos suele recuperar entre 5% y 15% de los carritos.
  - Con el volumen actual son 1 o 2 pedidos más al mes, casi sin costo.

## 1. Recuperación de carrito: 3 correos

| # | Cuándo | Asunto | Objetivo |
|---|--------|--------|----------|
| 1 | 1 h | Tu jersey te está esperando ⚽ | Recordatorio con el carrito exacto |
| 2 | 24 h | ¿Te quedó alguna duda? (+3,000 pedidos entregados) | Quitar la desconfianza: pago seguro, rastreo, foto real, tallas |
| 3 | 72 h | Última llamada: tu carrito sigue guardado | Cierre + upsell a 5 jerseys con el código 5X3 |

Asuntos alternativos para probar (A/B):
- 1: "{nombre}, ¿se te olvidó algo?" · "Tus 3 jerseys siguen en el carrito"
- 2: "Así llega tu jersey (foto real)"
- 3: "Lleva 5, paga 3 — solo con este código"

### Cómo instalarlo

**Opción A, la más fácil. Recomendada.**
1. Ve a Crecimiento > Automatizaciones (antes "Marketing"; también aparece en la app Messaging, antes "Shopify Email") > Crear automatización > plantilla "Recuperar pago abandonado".
2. Deja la primera espera en 1 h. Agrega "Esperar 1 día" + correo 2, y "Esperar 2 días" + correo 3.
   - La plantilla deja de enviar sola si el cliente compra.
3. En cada correo del editor de Shopify Email:
   - Usa el bloque de productos del carrito, que ya viene en la plantilla.
   - Pon el título, el texto, el botón y el asunto de los archivos `out/0X-*.html`.
   - Usa fondo negro `#0A0A0B`, botones rojo `#FF1E2D` y el logo `ff-logo-email.jpg`.
4. **Importante:**
   - Para no mandar dos correos, desactiva el correo automático de Configuración > Pago y envío (checkout) > "Pagos abandonados".
   - O usa solo la opción B.

**Opción B: correo 1 con el diseño exacto (código).**
1. Ve a Configuración > Notificaciones > Notificaciones para clientes > "Pago abandonado" > Editar código.
2. Pega todo `out/01-recordatorio-1h.liquid`.
   - Ya trae el carrito real del cliente: fotos, tallas, precios y el link `{{ url }}` que lo recupera.
3. En Configuración > Pago y envío > Pagos abandonados, elige enviar a "Cualquiera que abandone el pago" después de 1 hora.
4. Los correos 2 y 3 se arman con la automatización de la opción A, sin su primer correo.

En cualquier caso, usa "Vista previa" y mándate un correo de prueba antes de activar.

## 2. ¿Vale la pena hacer email marketing para generar pedidos? Sí.

Mandarle correo a 368 personas que ya te conocen cuesta casi nada; Shopify Email incluye 10,000 envíos al mes.
- Un ad en Meta paga por cada vista; el correo no.
- Una lista de clientes y suscriptores suele abrir 30–45% y convertir 1–3%.
- Con el ticket de $1,600 del 3x2, una campaña puede pagar el mes con 1 o 2 pedidos.

### Calendario sugerido (1 correo por semana, no más)

| Fecha | Campaña | Gancho |
|-------|---------|--------|
| Jue 29 oct | **Las 3 del Madrid por $1,600** (`promo-01`) | Post-Clásico, 3x2 |
| Jue 5 nov | Leyendas retro | Retro del Madrid, Barça y Selección; el código RETRO10 aplica en retro |
| Lun 9 nov | Aviso Buen Fin: "Prepárate" | Lista de deseos y tallas; sin descuento todavía |
| Buen Fin (mediados de nov, confirma fechas) | 5X3 (5 por $2,400) | Única vez al año con urgencia real |
| Inicio de dic | Regalo navideño | "Llega antes del 24 si pides antes del X" |
| Fecha FIFA / Selección | Selección Mexicana | Mundial 2026 sigue vendiendo |

Hora de envío: martes a jueves, 7–9 pm (hora CDMX), cuando la gente revisa el cel.

### Automatizaciones fijas, que corren solas

1. **Bienvenida** (nuevo suscriptor del popup):
   - Correo 1 al instante: el código del popup y cómo funciona el 3x2.
   - Correo 2 a los 2 días: más vendidas y foto real de cliente.
2. **Post-compra:**
   - A los 3 días: "tu pedido va en camino", con rastreo y talla.
   - A los 15 días: "¿Ya te llegó? Mándanos foto y te damos 10% en tu próxima". Así juntas reseñas y fotos reales para los ads.
3. **Recuperar cliente:** a los 60 días sin comprar, un "Te extrañamos" con las novedades de la temporada.

### Reglas para que no caigan en spam ni te den de baja

- Máximo 1 campaña por semana. Asuntos sin MAYÚSCULAS completas ni demasiados emojis.
- No inventes escasez: los textos dicen que M y L son las tallas más pedidas, no que "quedan 2".
- Ve a Configuración > Notificaciones > "Autenticación de dominio de remitente" y autentica footballfrenzy.shop.
  - Sin eso, Gmail manda los correos a Promociones o a Spam.
- Revisa que el dato de "+3,000 pedidos entregados" se pueda respaldar, igual que en los ads.
