"""Emails de Football Frenzy Shop: recuperación de carrito (3 correos) + campaña promocional.

Salida en emails/out/:
  01-recordatorio-1h.liquid        -> pegar en Configuración > Notificaciones > Pago abandonado (código Liquid real)
  01-recordatorio-1h-preview.html  -> el mismo correo con un carrito de ejemplo (para ver cómo se ve)
  02-confianza-24h.html            -> segundo correo (24 h)
  03-ultima-llamada-72h.html       -> tercer correo (72 h)
  promo-01-real-madrid-3x2.html    -> campaña a toda la lista
Uso: python3 build.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
OUT = HERE + "out/"
CDN = "https://cdn.shopify.com/s/files/1/0948/5919/8780/files/"
LOGO = CDN + "ff-logo-email.jpg?v=1793062975"
SHOP = "https://footballfrenzy.shop"
WA = "https://wa.me/525512941852"
RED, BLACK, CARD, SOFT = "#FF1E2D", "#0A0A0B", "#16161A", "#B9B9C0"
HEAD = "'Anton', Impact, 'Arial Narrow Bold', 'Arial Black', sans-serif"
BODY = "Helvetica, Arial, sans-serif"


def page(title, preheader, inner):
    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark"><meta name="supported-color-schemes" content="dark">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Anton&display=swap" rel="stylesheet">
<style>
  body{{margin:0;padding:0;background:{BLACK};}}
  a{{color:{RED};}}
  @media (max-width:620px){{ .w{{width:100%!important;}} .px{{padding-left:20px!important;padding-right:20px!important;}} .h1{{font-size:40px!important;line-height:44px!important;}} .col{{display:block!important;width:100%!important;}} }}
</style></head>
<body style="margin:0;padding:0;background:{BLACK};">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">{preheader}&#8202;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{BLACK};">
<tr><td align="center" style="padding:24px 12px;">
<table role="presentation" class="w" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px;max-width:600px;background:{BLACK};">
<tr><td align="center" style="padding:8px 0 20px;"><a href="{SHOP}"><img src="{LOGO}" width="110" height="110" alt="Football Frenzy Shop" style="display:block;border:0;border-radius:55px;"></a></td></tr>
{inner}
{footer()}
</table></td></tr></table></body></html>
"""


def kicker(s):
    return f'<tr><td align="center" class="px" style="padding:0 40px 6px;font:700 13px/18px {BODY};letter-spacing:4px;color:{RED};text-transform:uppercase;">{s}</td></tr>'


def h1(s):
    return f'<tr><td align="center" class="px h1" style="padding:0 40px 14px;font:400 48px/52px {HEAD};color:#FFFFFF;text-transform:uppercase;letter-spacing:.5px;">{s}</td></tr>'


def p(s, color="#E8E8EC", size=17, pad="0 48px 16px"):
    return f'<tr><td align="center" class="px" style="padding:{pad};font:400 {size}px/26px {BODY};color:{color};">{s}</td></tr>'


def button(label, href, pad="10px 40px 26px"):
    return f"""<tr><td align="center" style="padding:{pad};">
<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
<td align="center" bgcolor="{RED}" style="border-radius:10px;">
<a href="{href}" style="display:inline-block;padding:18px 38px;font:400 22px/24px {HEAD};letter-spacing:1px;color:#FFFFFF;text-decoration:none;text-transform:uppercase;border-radius:10px;">{label}</a>
</td></tr></table></td></tr>"""


def wa_link(pad="0 40px 24px"):
    return p(f'¿Dudas con la talla o el dorsal? <a href="{WA}" style="color:#FFFFFF;font-weight:700;">Escríbenos por WhatsApp</a> y te ayudamos en minutos.', SOFT, 15, pad)


def perks():
    items = (("ENVÍO GRATIS", "A todo México"), ("3X2", "Automático en el carrito"), ("RASTREO", "En cada pedido"))
    cells = "".join(
        f'<td class="col" width="33%" align="center" style="padding:14px 6px;border-top:1px solid #2A2A30;">'
        f'<div style="font:400 20px/24px {HEAD};color:#FFFFFF;letter-spacing:.5px;">{a}</div>'
        f'<div style="font:400 13px/18px {BODY};color:{SOFT};">{b}</div></td>' for a, b in items)
    return f'<tr><td style="padding:6px 24px 10px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>{cells}</tr></table></td></tr>'


def footer():
    return f"""<tr><td align="center" style="padding:26px 40px 8px;border-top:1px solid #2A2A30;font:400 13px/20px {BODY};color:#8A8A92;">
<a href="{SHOP}" style="color:#FFFFFF;text-decoration:none;font-weight:700;">FOOTBALLFRENZY.SHOP</a> &nbsp;·&nbsp; <a href="https://www.instagram.com/footballfrenzy.shop" style="color:#8A8A92;">Instagram</a> &nbsp;·&nbsp; <a href="{WA}" style="color:#8A8A92;">WhatsApp</a><br>
Tallas S a 4XL · Entrega de 7 a 13 días hábiles · Pagos seguros
</td></tr>
<tr><td align="center" style="padding:6px 40px 20px;font:400 12px/18px {BODY};color:#6A6A72;">{{{{ unsubscribe }}}}</td></tr>"""


# ------------------------------------------------------------------ cart block

ROW = """<tr>
<td width="96" style="padding:12px 0 12px 16px;"><img src="__IMG__" width="80" height="80" alt="" style="display:block;border-radius:8px;background:#fff;object-fit:cover;"></td>
<td style="padding:12px 10px;font:700 15px/20px __BODY__;color:#FFFFFF;">__TITLE__<div style="font:400 13px/18px __BODY__;color:__SOFT__;">__VARIANT__Cantidad: __QTY__</div></td>
<td align="right" style="padding:12px 16px 12px 0;font:700 15px/20px __BODY__;color:#FFFFFF;white-space:nowrap;">__PRICE__</td>
</tr>"""


def cart(rows, subtotal):
    return f"""<tr><td style="padding:4px 24px 18px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{CARD};border-radius:14px;border:1px solid #2A2A30;">
<tr><td colspan="3" style="padding:16px 16px 4px;font:700 12px/16px {BODY};letter-spacing:3px;color:{RED};">TU CARRITO</td></tr>
{rows}
<tr><td colspan="2" style="padding:14px 16px;border-top:1px solid #2A2A30;font:700 15px/20px {BODY};color:{SOFT};">Subtotal (ya con descuentos)</td>
<td align="right" style="padding:14px 16px;border-top:1px solid #2A2A30;font:400 24px/26px {HEAD};color:#FFFFFF;white-space:nowrap;">{subtotal}</td></tr>
</table></td></tr>"""


def row(img, title, variant, qty, price):
    s = ROW.replace("__BODY__", BODY).replace("__SOFT__", SOFT)
    return s.replace("__IMG__", img).replace("__TITLE__", title).replace("__VARIANT__", variant).replace("__QTY__", qty).replace("__PRICE__", price)


LIQUID_ROWS = "{% for line in line_items %}\n" + row(
    "{% if line.image %}{{ line.image | image_url: width: 160 }}{% endif %}",
    "{{ line.product.title | default: line.title }}",
    "{% if line.variant.title and line.variant.title != 'Default Title' %}Talla: {{ line.variant.title }} · {% endif %}",
    "{{ line.quantity }}",
    "{{ line.final_line_price | money }}") + "\n{% endfor %}"

SAMPLE = [
    (CDN + "bd0afa71fa.jpg?v=1791358335", "25/26 Real Madrid CF away", "Talla: M · ", "1", "$800.00"),
    (CDN + "6b87ac7d16.jpg?v=1791358297", "25/26 Real Madrid CF third", "Talla: M · ", "1", "$800.00"),
    (CDN + "867e91d5b7_35ef9467-54c1-4bf1-b8fe-d6a81d24b0f9.jpg?v=1791358297", "25/26 Real Madrid CF home", "Talla: M · ", "1", "$0.00 (3x2)"),
]
SAMPLE_ROWS = "\n".join(row(*r) for r in SAMPLE)


# ------------------------------------------------------------------ correo 1 (1 h): recordatorio

def email1(rows, subtotal, name, url):
    inner = (kicker("Se te quedó algo")
             + h1("Tu jersey te está esperando")
             + p(f"Hola {name}, vimos que dejaste tu pedido a medias. Lo guardamos tal como lo dejaste: mismas tallas, mismo 3x2, nada que volver a elegir.")
             + cart(rows, subtotal)
             + button("Terminar mi pedido", url)
             + perks()
             + wa_link("8px 40px 24px"))
    return page("Tu jersey te está esperando", "Guardamos tu carrito tal como lo dejaste. Termina tu pedido en 1 clic.", inner)


LIQUID_NAME = "{{ billing_address.first_name | default: customer.first_name | default: 'crack' }}"
LIQUID_HEADER = """{% comment %}
  Football Frenzy Shop — Pago abandonado (correo 1).
  Pegar completo en: Configuración > Notificaciones > Notificaciones para clientes > Pago abandonado > Editar código.
  {{ url }} = link que recupera el carrito exacto del cliente.
{% endcomment %}
"""


# ------------------------------------------------------------------ correo 2 (24 h): confianza

PROOF = CDN + "ff-cliente-email.jpg?v=1793063153"


def email2(url):
    stats = (("+3,000", "pedidos entregados"), ("7-13", "días hábiles a tu puerta"), ("S-4XL", "todas las tallas"))
    cells = "".join(
        f'<td class="col" width="33%" align="center" style="padding:16px 6px;"><div style="font:400 34px/38px {HEAD};color:{RED};">{a}</div>'
        f'<div style="font:400 13px/18px {BODY};color:{SOFT};">{b}</div></td>' for a, b in stats)
    faq = (("¿Es seguro pagar?", "Sí. El pago se procesa en el checkout de Shopify, cifrado. Nunca vemos los datos de tu tarjeta."),
           ("¿Cómo sé dónde va mi pedido?", "Te mandamos número de rastreo por correo en cuanto sale, y lo puedes seguir en cualquier momento."),
           ("¿Y si no me queda la talla?", "Escríbenos antes de pagar y te decimos la talla exacta según tu estatura y peso."))
    faq_html = "".join(
        f'<tr><td class="px" style="padding:0 48px 14px;"><div style="font:700 16px/22px {BODY};color:#FFFFFF;">{q}</div>'
        f'<div style="font:400 15px/22px {BODY};color:{SOFT};">{a}</div></td></tr>' for q, a in faq)
    inner = (kicker("Sin letras chiquitas")
             + h1("¿Te quedó alguna duda?")
             + p("Comprar en línea da desconfianza, lo entendemos. Por eso te contamos cómo trabajamos antes de que termines tu pedido.")
             + f'<tr><td style="padding:0 24px 10px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{CARD};border-radius:14px;"><tr>{cells}</tr></table></td></tr>'
             + f'<tr><td align="center" style="padding:16px 40px 6px;"><img src="__PROOF__" width="300" alt="Cliente con su jersey de Football Frenzy" style="display:block;width:100%;max-width:300px;border-radius:14px;border:6px solid #FFFFFF;"></td></tr>'
             + p("Foto real de cliente. Así llega tu pedido.", SOFT, 13, "6px 40px 22px")
             + faq_html
             + button("Volver a mi carrito", url, "14px 40px 22px")
             + wa_link())
    return page("¿Te quedó alguna duda?", "Pago seguro, rastreo en cada pedido y +3,000 entregas. Tu carrito sigue guardado.", inner)


# ------------------------------------------------------------------ correo 3 (72 h): última llamada

def email3(url):
    box = (f'<tr><td style="padding:6px 24px 18px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{CARD};border:2px solid {RED};border-radius:14px;">'
           f'<tr><td align="center" style="padding:22px 20px 6px;font:700 12px/16px {BODY};letter-spacing:3px;color:{RED};">¿VAS POR MÁS?</td></tr>'
           f'<tr><td align="center" style="padding:0 20px 4px;font:400 36px/40px {HEAD};color:#FFFFFF;">LLEVA 5 Y PAGA 3</td></tr>'
           f'<tr><td align="center" style="padding:0 24px 8px;font:400 15px/22px {BODY};color:{SOFT};">Agrega 2 jerseys más y usa el código</td></tr>'
           f'<tr><td align="center" style="padding:4px 20px 8px;"><span style="display:inline-block;padding:10px 26px;border:2px dashed #FFFFFF;border-radius:8px;font:400 30px/32px {HEAD};letter-spacing:4px;color:#FFFFFF;">5X3</span></td></tr>'
           f'<tr><td align="center" style="padding:4px 24px 22px;font:400 14px/20px {BODY};color:{SOFT};">5 jerseys de $800 por <b style="color:#FFFFFF;">$2,400</b> ($480 c/u). El código reemplaza al 3x2 automático.</td></tr>'
           f'</table></td></tr>')
    inner = (kicker("Último aviso")
             + h1("Última llamada para tu pedido")
             + p("Tu carrito sigue guardado, pero el inventario no se aparta hasta que pagas. Las tallas M y L de esta temporada son las más pedidas: si la quieres, este es el momento.")
             + button("Recuperar mi pedido", url, "6px 40px 24px")
             + box
             + perks()
             + wa_link("8px 40px 24px"))
    return page("Última llamada para tu pedido", "Tu carrito sigue guardado. Y si llevas 5, pagas 3 con el código 5X3.", inner)


# ------------------------------------------------------------------ campaña: Real Madrid 3x2

RM = [(CDN + "bd0afa71fa.jpg?v=1791358335", "Visitante 25/26", SHOP + "/products/25-26-season-real-madrid-cf-away-long-sleeved-fan-version"),
      (CDN + "6b87ac7d16.jpg?v=1791358297", "Tercera 25/26", SHOP + "/products/25-26-season-real-madrid-cf-third-long-sleeved-fan-version"),
      (CDN + "903ded4008.jpg?v=1791358375", "Retro 11/12", SHOP + "/products/11-12-season-real-madrid-cf-away-retro-fan-version")]


def promo_rm():
    cells = "".join(
        f'<td class="col" width="33%" align="center" valign="top" style="padding:8px 6px;"><a href="{u}" style="text-decoration:none;">'
        f'<img src="{i}" width="170" alt="{t}" style="display:block;width:100%;max-width:170px;border-radius:10px;background:#fff;">'
        f'<div style="padding-top:8px;font:400 18px/22px {HEAD};color:#FFFFFF;letter-spacing:.5px;">{t.upper()}</div>'
        f'<div style="font:400 14px/20px {BODY};color:{SOFT};">$800</div></a></td>' for i, t, u in RM)
    inner = (kicker("Real Madrid · Temporada 25/26 y retro")
             + h1("Las 3 del Madrid por $1,600")
             + p("Elige 3 jerseys, paga 2. El descuento se aplica solo en el carrito: sin códigos, sin trucos. Salen en $533 cada una con envío gratis.")
             + button("Arma tu 3x2", SHOP + "/collections/real-madrid", "4px 40px 22px")
             + f'<tr><td style="padding:0 18px 12px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>{cells}</tr></table></td></tr>'
             + p("¿Eres del Barça, del América o de la Selección? El 3x2 aplica en todas las jerseys de la tienda, y puedes combinar equipos.", SOFT, 15, "8px 48px 18px")
             + perks()
             + wa_link("8px 40px 24px"))
    return page("Las 3 del Madrid por $1,600", "3x2 automático en todas las jerseys. Salen en $533 c/u con envío gratis.", inner)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    liquid = LIQUID_HEADER + email1(LIQUID_ROWS, "{{ subtotal_price | money }}", LIQUID_NAME, "{{ url }}")
    liquid = liquid.replace("{{ unsubscribe }}", "Recibes este correo porque iniciaste un pedido en footballfrenzy.shop.")
    files = {
        "01-recordatorio-1h.liquid": liquid,
        "01-recordatorio-1h-preview.html": email1(SAMPLE_ROWS, "$1,600.00", "Diego", SHOP),
        "02-confianza-24h.html": email2(SHOP + "/cart").replace("__PROOF__", PROOF),
        "03-ultima-llamada-72h.html": email3(SHOP + "/cart"),
        "promo-01-real-madrid-3x2.html": promo_rm(),
    }
    for n, s in files.items():
        if not n.endswith(".liquid"):
            s = s.replace("{{ unsubscribe }}", "Si ya no quieres recibir estos correos, puedes darte de baja aquí.")
        open(OUT + n, "w").write(s)
        print(n, len(s))
