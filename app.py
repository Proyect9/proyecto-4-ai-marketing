from flask import Flask, request
from google import genai
from dotenv import load_dotenv
from html import escape
import json
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
app = Flask(__name__)

ESTILO_FORM = """
<style>
    body { font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; background-color: #f5f5f5; }
    h1 { color: #1F4E79; }
    form { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    label { display: block; margin-top: 12px; font-weight: bold; }
    input, select { width: 100%; padding: 8px; margin-top: 4px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
    button { margin-top: 20px; padding: 12px 25px; background-color: #2E75B6; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; }
    button:hover { background-color: #1F4E79; }
    a { color: #2E75B6; }
</style>
"""

ESTILO_RESULTADO = """
<style>
    body { font-family: Arial, sans-serif; max-width: 700px; margin: 40px auto; padding: 20px; background-color: #f5f5f5; }
    h1 { color: #1F4E79; }
    .caja { background: white; padding: 20px; border-radius: 10px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    a { color: #2E75B6; }
</style>
"""

@app.route("/")
def inicio():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Marketing Content System</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 700px; margin: 50px auto; padding: 20px; background-color: #f5f5f5; }
            h1 { color: #1F4E79; }
            .menu { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            .opcion { display: block; padding: 12px 18px; margin: 10px 0; background-color: #2E75B6; color: white; text-decoration: none; border-radius: 6px; font-size: 16px; }
            .opcion:hover { background-color: #1F4E79; }
        </style>
    </head>
    <body>
        <h1>AI Marketing Content System</h1>
        <p>Proyecto 4 — Versión Web</p>
        <div class="menu">
            <h2>Elige una opción:</h2>
            <a class="opcion" href="/v2">V2 — Generador de Contenido</a>
            <a class="opcion" href="/v3">V3 — Planificador de 7 días</a>
            <a class="opcion" href="/v4">V4 — Analizar una publicación</a>
        </div>
    </body>
    </html>
    """

@app.route("/v2", methods=["GET", "POST"])
def v2():
    if request.method == "GET":
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>V2 - Generador de contenido</title>
            """ + ESTILO_FORM + """
        </head>
        <body>
            <h1>V2 — Generador de contenido</h1>
            <p><a href="/">← Volver al inicio</a></p>
            <form method="POST">
                <label>Nombre del negocio</label>
                <input type="text" name="nombre" required>
                <label>Tipo de negocio (ej: Cafetería)</label>
                <input type="text" name="tipo" required>
                <label>Productos (separados por coma)</label>
                <input type="text" name="productos" required>
                <label>Público objetivo</label>
                <input type="text" name="publico" required>
                <label>Ubicación</label>
                <input type="text" name="ubicacion" required>
                <label>Objetivo de marketing</label>
                <input type="text" name="objetivo" required>
                <label>Plataforma (ej: Instagram)</label>
                <input type="text" name="plataforma" required>
                <label>Tono de comunicación</label>
                <input type="text" name="tono" required>
                <label>Promoción actual (opcional)</label>
                <input type="text" name="promocion">
                <label>¿Cuántas ideas quieres?</label>
                <select name="cantidad">
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3" selected>3</option>
                </select>
                <button type="submit">Generar ideas</button>
            </form>
        </body>
        </html>
        """
    else:
        name = request.form["nombre"]
        tipo = request.form["tipo"]
        productos_texto = request.form["productos"]
        audience = request.form["publico"]
        location = request.form["ubicacion"]
        objective = request.form["objetivo"]
        platform = request.form["plataforma"]
        tone = request.form["tono"]
        promotion = request.form.get("promocion", "")
        cantidad = int(request.form["cantidad"])
        products = [p.strip() for p in productos_texto.split(",") if p.strip() != ""]
        business_data = {
            "name": name,
            "type": tipo,
            "products": products,
            "audience": audience,
            "location": location,
            "objective": objective,
            "platform": platform,
            "tone": tone,
            "promotion": promotion
        }
        prompt = f"""
Eres un experto en marketing digital para pequeños negocios.
Analiza los datos del negocio y genera exactamente {cantidad} propuestas de contenido diferentes.
Responde ÚNICAMENTE con un JSON válido.
No escribas texto antes ni después del JSON. No uses ```json.

Datos del negocio:
{json.dumps(business_data, ensure_ascii=False, indent=2)}

Reglas:
- Escribe todo en español claro y profesional.
- Genera exactamente {cantidad} ideas de contenido.
- recommended_content_type de cada idea debe ser solo UN formato (Reel, Carrusel, Story, Post estático).
- Los hashtags deben empezar con el símbolo #.

Devuelve exactamente este formato:
{{
  "business_summary": "",
  "target_audience_profile": "",
  "marketing_objective": "",
  "content_ideas": [
    {{
      "recommended_content_type": "",
      "content_idea": "",
      "why_this_works": "",
      "hook": "",
      "caption": "",
      "call_to_action": "",
      "hashtags": [],
      "visual_concept": ""
    }}
  ]
}}
"""
        resultado = None
        for intento in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt
                )
                datos = json.loads(response.text)
                if len(datos["content_ideas"]) == cantidad:
                    resultado = datos
                    break
            except Exception:
                pass
        if resultado is None:
            return "<h1>Error</h1><p>No se pudieron generar las ideas. Intenta de nuevo.</p><p><a href='/v2'>Volver</a></p>"
        with open("analisis_v2.json", "w", encoding="utf-8") as f:
            json.dump(resultado, f, indent=4, ensure_ascii=False)
        ideas_html = ""
        for i, idea in enumerate(resultado["content_ideas"], 1):
            hashtags = " ".join(h if h.startswith("#") else "#" + h for h in idea["hashtags"])
            ideas_html += f"""
            <div class="caja">
                <h3>Idea {i} — {escape(idea['recommended_content_type'])}</h3>
                <p><strong>Idea:</strong> {escape(idea['content_idea'])}</p>
                <p><strong>Por qué funciona:</strong> {escape(idea['why_this_works'])}</p>
                <p><strong>Hook:</strong> {escape(idea['hook'])}</p>
                <p><strong>Caption:</strong> {escape(idea['caption'])}</p>
                <p><strong>CTA:</strong> {escape(idea['call_to_action'])}</p>
                <p><strong>Hashtags:</strong> {escape(hashtags)}</p>
                <p><strong>Concepto visual:</strong> {escape(idea['visual_concept'])}</p>
            </div>
            """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Resultado V2</title>
            {ESTILO_RESULTADO}
        </head>
        <body>
            <h1>Ideas de contenido</h1>
            <p><a href="/v2">← Generar otras</a> | <a href="/">Inicio</a></p>
            <div class="caja">
                <h3>Resumen del negocio</h3>
                <p>{escape(resultado['business_summary'])}</p>
                <h3>Público objetivo</h3>
                <p>{escape(resultado['target_audience_profile'])}</p>
                <h3>Objetivo de marketing</h3>
                <p>{escape(resultado['marketing_objective'])}</p>
            </div>
            {ideas_html}
        </body>
        </html>
        """

@app.route("/v3", methods=["GET", "POST"])
def v3():
    if request.method == "GET":
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>V3 - Planificador de 7 días</title>
            """ + ESTILO_FORM + """
        </head>
        <body>
            <h1>V3 — Planificador de 7 días</h1>
            <p><a href="/">← Volver al inicio</a></p>
            <form method="POST">
                <label>Nombre del negocio</label>
                <input type="text" name="nombre" required>
                <label>Tipo de negocio (ej: Cafetería)</label>
                <input type="text" name="tipo" required>
                <label>Productos (separados por coma)</label>
                <input type="text" name="productos" required>
                <label>Público objetivo</label>
                <input type="text" name="publico" required>
                <label>Ubicación</label>
                <input type="text" name="ubicacion" required>
                <label>Objetivo de marketing</label>
                <input type="text" name="objetivo" required>
                <label>Plataforma (ej: Instagram)</label>
                <input type="text" name="plataforma" required>
                <label>Tono de comunicación</label>
                <input type="text" name="tono" required>
                <label>Promoción actual (opcional)</label>
                <input type="text" name="promocion">
                <button type="submit">Generar plan de 7 días</button>
            </form>
        </body>
        </html>
        """
    else:
        name = request.form["nombre"]
        tipo = request.form["tipo"]
        productos_texto = request.form["productos"]
        audience = request.form["publico"]
        location = request.form["ubicacion"]
        objective = request.form["objetivo"]
        platform = request.form["plataforma"]
        tone = request.form["tono"]
        promotion = request.form.get("promocion", "")
        products = [p.strip() for p in productos_texto.split(",") if p.strip() != ""]
        business_data = {
            "name": name,
            "type": tipo,
            "products": products,
            "audience": audience,
            "location": location,
            "objective": objective,
            "platform": platform,
            "tone": tone,
            "promotion": promotion
        }
        prompt = f"""
Eres un experto en marketing digital para pequeños negocios.
Analiza los datos del negocio y crea un plan de contenido de 7 días, con exactamente una publicación por día.
Responde ÚNICAMENTE con un JSON válido.
No escribas texto antes ni después del JSON. No uses ```json.

Datos del negocio:
{json.dumps(business_data, ensure_ascii=False, indent=2)}

Reglas:
- Escribe todo en español claro y profesional.
- Genera exactamente 7 publicaciones, una por día (day 1 al 7), sin días de descanso.
- Varía los formatos durante la semana (Reel, Carrusel, Story, Post estático).
- recommended_content_type debe ser solo UN formato por día.
- Los hashtags deben empezar con el símbolo #.

Devuelve exactamente este formato:
{{
  "business_summary": "",
  "weekly_strategy": "",
  "content_plan": [
    {{
      "day": 1,
      "recommended_content_type": "",
      "content_idea": "",
      "hook": "",
      "caption": "",
      "call_to_action": "",
      "hashtags": [],
      "visual_concept": ""
    }}
  ]
}}
"""
        resultado = None
        for intento in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt
                )
                datos = json.loads(response.text)
                if len(datos["content_plan"]) == 7:
                    resultado = datos
                    break
            except Exception:
                pass
        if resultado is None:
            return "<h1>Error</h1><p>No se pudo generar el plan después de 3 intentos. Intenta de nuevo.</p><p><a href='/v3'>Volver</a></p>"
        nombre_limpio = "".join(c for c in name.lower() if c.isalnum() or c == " ").strip().replace(" ", "_")
        if nombre_limpio == "":
            nombre_limpio = "negocio"
        nombre_archivo = f"plan_{nombre_limpio}.json"
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            json.dump(resultado, f, indent=4, ensure_ascii=False)
        dias_html = ""
        for publicacion in resultado["content_plan"]:
            hashtags = " ".join(h if h.startswith("#") else "#" + h for h in publicacion["hashtags"])
            dias_html += f"""
            <div class="caja">
                <h3>Día {escape(str(publicacion['day']))} — {escape(publicacion['recommended_content_type'])}</h3>
                <p><strong>Idea:</strong> {escape(publicacion['content_idea'])}</p>
                <p><strong>Hook:</strong> {escape(publicacion['hook'])}</p>
                <p><strong>Caption:</strong> {escape(publicacion['caption'])}</p>
                <p><strong>CTA:</strong> {escape(publicacion['call_to_action'])}</p>
                <p><strong>Hashtags:</strong> {escape(hashtags)}</p>
                <p><strong>Concepto visual:</strong> {escape(publicacion['visual_concept'])}</p>
            </div>
            """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Resultado V3</title>
            {ESTILO_RESULTADO}
        </head>
        <body>
            <h1>Plan de contenido de 7 días</h1>
            <p><a href="/v3">← Generar otro plan</a> | <a href="/">Inicio</a></p>
            <div class="caja">
                <h3>Resumen del negocio</h3>
                <p>{escape(resultado["business_summary"])}</p>
                <h3>Estrategia semanal</h3>
                <p>{escape(resultado["weekly_strategy"])}</p>
                <p><em>Guardado como: {escape(nombre_archivo)}</em></p>
            </div>
            {dias_html}
        </body>
        </html>
        """

@app.route("/v4", methods=["GET", "POST"])
def v4():
    if request.method == "GET":
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>V4 - Analizar publicación</title>
            """ + ESTILO_FORM + """
        </head>
        <body>
            <h1>V4 — Analizar una publicación</h1>
            <p><a href="/">← Volver al inicio</a></p>
            <form method="POST">
                <label>Formato (Reel, Carrusel, Story...)</label>
                <input type="text" name="formato" required>
                <label>Plataforma (Instagram, TikTok...)</label>
                <input type="text" name="plataforma" required>
                <label>Likes</label>
                <input type="number" name="likes" required>
                <label>Comentarios</label>
                <input type="number" name="comentarios" required>
                <label>Compartidos</label>
                <input type="number" name="compartidos" required>
                <label>Guardados</label>
                <input type="number" name="guardados" required>
                <label>Alcance</label>
                <input type="number" name="alcance" required>
                <label>Seguidores de la cuenta</label>
                <input type="number" name="seguidores" required>
                <button type="submit">Analizar publicación</button>
            </form>
        </body>
        </html>
        """
    else:
        formato = request.form["formato"]
        plataforma = request.form["plataforma"]
        likes = int(request.form["likes"])
        comentarios = int(request.form["comentarios"])
        compartidos = int(request.form["compartidos"])
        guardados = int(request.form["guardados"])
        alcance = int(request.form["alcance"])
        seguidores = int(request.form["seguidores"])
        interacciones = likes + comentarios + compartidos + guardados
        engagement = round((interacciones / alcance) * 100, 2) if alcance > 0 else 0
        metricas = {
            "formato": formato,
            "plataforma": plataforma,
            "likes": likes,
            "comentarios": comentarios,
            "compartidos": compartidos,
            "guardados": guardados,
            "alcance": alcance,
            "seguidores": seguidores,
            "engagement_porcentaje": engagement
        }
        prompt = f"""
Eres un experto en análisis de contenido de redes sociales para pequeños negocios.
Analiza las métricas de ESTA publicación y responde ÚNICAMENTE con un JSON válido.
No escribas texto antes ni después del JSON. No uses ```json.

Métricas:
{json.dumps(metricas, ensure_ascii=False, indent=2)}

Devuelve exactamente este formato:
{{
  "resumen_desempeno": "",
  "que_funciono": "",
  "que_no_funciono": "",
  "recomendaciones": ["", "", ""]
}}
"""
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )
            resultado = json.loads(response.text)
            resultado_completo = {
                "metricas_originales": metricas,
                "analisis": resultado
            }
            with open("analisis_v4.json", "w", encoding="utf-8") as f:
                json.dump(resultado_completo, f, indent=4, ensure_ascii=False)
            recomendaciones_html = "".join([f"<li>{escape(r)}</li>" for r in resultado["recomendaciones"]])
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Resultado V4</title>
                {ESTILO_RESULTADO}
            </head>
            <body>
                <h1>Análisis de la publicación</h1>
                <p><a href="/v4">← Analizar otra</a> | <a href="/">Inicio</a></p>
                <div class="caja">
                    <strong>Engagement calculado:</strong> {engagement}%
                </div>
                <div class="caja">
                    <h3>Resumen de desempeño</h3>
                    <p>{escape(resultado["resumen_desempeno"])}</p>
                </div>
                <div class="caja">
                    <h3>Qué funcionó</h3>
                    <p>{escape(resultado["que_funciono"])}</p>
                </div>
                <div class="caja">
                    <h3>Qué no funcionó</h3>
                    <p>{escape(resultado["que_no_funciono"])}</p>
                </div>
                <div class="caja">
                    <h3>3 Recomendaciones</h3>
                    <ul>{recomendaciones_html}</ul>
                </div>
            </body>
            </html>
            """
        except Exception as e:
            return f"<h1>Error</h1><p>{escape(str(e))}</p><p><a href='/v4'>Intentar de nuevo</a></p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))) 