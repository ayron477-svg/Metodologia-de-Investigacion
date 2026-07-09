import requests
from datetime import datetime
import re

def extraer_por_rango_experiencia(busqueda, rango_tipo):
    # Pedimos el máximo de 100 ofertas 
    url = f"https://www.getonbrd.com/api/v0/search/jobs?query={busqueda}&per_page=100"
    
    print(f"Conectando a la API para '{busqueda}' -> Buscando rango: {rango_tipo.upper()}...")
    respuesta = requests.get(url)
    
    if respuesta.status_code == 200:
        datos = respuesta.json()
        lista_ofertas = datos.get("data", [])
        
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        # El nombre del archivo indicará claramente si es Junior o 3-5 años
        nombre_archivo = f"datos_{rango_tipo}_{busqueda.replace(' ', '_')}_{fecha_hoy}.txt"
        
        tecnologias_clave = [
            "python", "java", "javascript", "typescript", "kotlin", "go", "golang", "ruby", "php", "c#", "c++", "swift",
            "react", "angular", "vue", "next.js", "node.js", "express", "spring", "springboot", "django", "laravel", "nestjs", "flutter",
            "sql", "postgres", "postgresql", "mysql", "mongodb", "oracle", "sqlserver", "redis", "firebase",
            "aws", "azure", "gcp", "docker", "kubernetes", "git", "github", "gitlab", "jenkins", "linux"
        ]
        
        # Ajustamos las palabras prohibidas según el rango
        if rango_tipo == "junior_hasta_2_anios":
            palabras_prohibidas = ["senior", "sr", "lead", "manager", "principal", "jefe", "expert"]
        else: # Para 3 a 5 años permitimos semi-senior, pero bloqueamos cargos de jefatura o senior estricto
            palabras_prohibidas = ["senior", "sr", "lead", "manager", "principal", "jefe", "expert"]

        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            archivo.write(f"--- REPORTE MERCADO: {busqueda.upper()} ({rango_tipo.upper()}) ---\n")
            archivo.write(f"Fecha de extracción: {fecha_hoy}\n")
            archivo.write("=" * 75 + "\n\n")
            
            contador = 1
            for oferta in lista_ofertas:
                atributos = oferta.get("attributes", {})
                titulo_trabajo = atributos.get("title", "Sin título")
                descripcion_completa = atributos.get("description", "")
                
                texto_analisis = (titulo_trabajo + " " + descripcion_completa).lower()
                
                # 1. FILTRO: Títulos excluidos
                if any(puro_sr in titulo_trabajo.lower() for puro_sr in palabras_prohibidas):
                    continue
                
                # 2. FILTRO MATEMÁTICO DE AÑOS
                desc_limpia_html = re.sub(r'<[^<]+?>', ' ', descripcion_completa).lower()
                coincidencias_anios = re.findall(r'(\d+)\s*(?:años|anios|años de experiencia|de experiencia)', desc_limpia_html)
                
                # Buscamos el número más alto de años que pide la oferta para clasificarla
                max_anios_detectados = 0
                for valor in coincidencias_anios:
                    anios = int(valor)
                    if anios > max_anios_detectados:
                        max_anios_detectados = anios
                
                # Lógica de división por rangos
                if rango_tipo == "junior_hasta_2_anios":
                    # Si detecta explícitamente más de 2 años, la descarta
                    if max_anios_detectados > 2:
                        continue
                elif rango_tipo == "experiencia_3_a_5_anios":
                    # Si no especifica años (0) o pide menos de 3, o pide más de 5, la descarta
                    if max_anios_detectados < 3 or max_anios_detectados > 5:
                        continue
                
                # 3. EXTRACCIÓN DE TECNOLOGÍAS
                techs_encontradas = []
                for tech in tecnologias_clave:
                    patron = r'\b' + re.escape(tech) + r'\b'
                    if re.search(patron, texto_analisis):
                        nombre_tech = "Go" if tech in ["go", "golang"] else tech.capitalize()
                        if nombre_tech not in techs_encontradas:
                            techs_encontradas.append(nombre_tech)
                
                # Guardar en el archivo de texto correspondiente
                archivo.write(f"Oferta {contador}: {titulo_trabajo} (Años detectados: {max_anios_detectados if max_anios_detectados > 0 else 'No especifica'})\n")
                if techs_encontradas:
                    archivo.write(f"Tecnologías detectadas: {', '.join(techs_encontradas)}\n")
                else:
                    archivo.write("Tecnologías detectadas: Ninguna del diccionario base\n")
                
                desc_ordenada = re.sub(r'\s+', ' ', desc_limpia_html).strip()
                archivo.write(f"Requisitos y Detalles: {desc_ordenada[:600]}...\n")
                archivo.write("-" * 60 + "\n")
                contador += 1
                
        print(f"¡Listo! Archivo guardado como: '{nombre_archivo}' con {contador - 1} ofertas.\n")
    else:
        print(f"Error al conectar con la API. Código: {respuesta.status_code}")


if __name__ == "__main__":
    busquedas_proyecto = ["informatica", "desarrollador", "software", "backend"]
    
    print("=== INICIANDO RECOLECCIÓN COMPARATIVA POR EXPERIENCIA ===\n")
    
    for termino in busquedas_proyecto:
        # Pasada 1: Genera los archivos de Juniors (0 a 2 años)
        extraer_por_rango_experiencia(termino, "junior_hasta_2_anios")
        
        # Pasada 2: Genera los archivos de Experiencia Media (3 a 5 años)
        extraer_por_rango_experiencia(termino, "experiencia_3_a_5_anios")
        
    print("=== PROCESO TERMINADO: Revisa tu carpeta para ver los archivos separados ===")
