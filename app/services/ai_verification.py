"""
AI Document Verification Service
Verifica documentos contra controles SOA usando diferentes proveedores de IA
"""
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import PyPDF2
import docx
import requests
from flask import current_app


class AIVerificationService:
    """Servicio de verificación de documentos usando IA"""

    def __init__(self):
        """Inicializa el servicio con la configuración"""
        self.enabled = current_app.config.get('AI_VERIFICATION_ENABLED', False)
        self.provider = current_app.config.get('AI_PROVIDER', 'ollama')
        self.model = current_app.config.get('AI_MODEL', 'llama3:8b')
        self.api_key = current_app.config.get('AI_API_KEY', '')
        self.base_url = current_app.config.get('AI_BASE_URL', 'http://localhost:11434')
        self.timeout = current_app.config.get('AI_TIMEOUT', 120)
        self.knowledge_path = current_app.config.get('KNOWLEDGE_BASE_PATH', 'knowledge')

    def is_available(self) -> Tuple[bool, str]:
        """
        Verifica si el servicio está disponible
        Returns: (is_available, message)
        """
        if not self.enabled:
            return False, "El servicio de verificación IA está deshabilitado"

        try:
            if self.provider == 'ollama':
                # Verificar que Ollama está corriendo
                response = requests.get(f"{self.base_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    return True, "Servicio Ollama disponible"
                return False, "Ollama no responde correctamente"

            elif self.provider in ['openai', 'deepseek']:
                if not self.api_key:
                    return False, f"API Key de {self.provider} no configurada"
                return True, f"Servicio {self.provider} configurado"

            else:
                return False, f"Proveedor '{self.provider}' no soportado"

        except Exception as e:
            return False, f"Error al verificar disponibilidad: {str(e)}"

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extrae texto de un archivo PDF"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error al extraer texto del PDF: {str(e)}")

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extrae texto de un archivo DOCX"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise Exception(f"Error al extraer texto del DOCX: {str(e)}")

    def extract_text_from_document(self, file_path: str) -> str:
        """Extrae texto de un documento según su extensión"""
        if not os.path.exists(file_path):
            raise Exception(f"Archivo no encontrado: {file_path}")

        ext = file_path.lower().split('.')[-1]

        if ext == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext in ['doc', 'docx']:
            return self.extract_text_from_docx(file_path)
        elif ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise Exception(f"Formato de archivo no soportado: {ext}")

    def load_knowledge_base(self) -> str:
        """Carga el contexto de la base de conocimiento (normas ISO, etc.)"""
        knowledge_text = ""

        if not os.path.exists(self.knowledge_path):
            return ""

        # Buscar archivos PDF de normas ISO
        for filename in os.listdir(self.knowledge_path):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(self.knowledge_path, filename)
                try:
                    # Extraer solo las primeras páginas para no saturar el contexto
                    with open(file_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        # Limitar a las primeras 10 páginas para resumen
                        max_pages = min(10, len(pdf_reader.pages))
                        for i in range(max_pages):
                            knowledge_text += pdf_reader.pages[i].extract_text() + "\n"
                except Exception as e:
                    current_app.logger.warning(f"No se pudo leer {filename}: {str(e)}")

        return knowledge_text[:10000]  # Limitar a 10k caracteres

    def build_verification_prompt(self, document_text: str, control: Dict, iso_context: str) -> str:
        """Construye el prompt para la verificación del control"""
        prompt = f"""Eres un auditor experto en ISO/IEC 27001. Tu tarea es verificar si un documento cumple con los requisitos de un control específico del Anexo A.

CONTEXTO ISO 27001:
{iso_context}

CONTROL A VERIFICAR:
ID: {control['control_id']}
Título: {control['title']}
Descripción: {control['description']}
Categoría: {control['category']}

DOCUMENTO A ANALIZAR:
{document_text[:5000]}

INSTRUCCIONES:
Analiza el documento y determina:
1. ¿El documento cubre los requisitos del control?
2. ¿Qué aspectos del control están cubiertos?
3. ¿Qué aspectos faltan o son insuficientes?
4. Proporciona citas específicas del documento como evidencia
5. Da recomendaciones de mejora

RESPONDE EN FORMATO JSON ESTRICTO:
{{
  "compliance_status": "compliant|partial|non_compliant",
  "confidence_level": 1-5,
  "overall_score": 0-100,
  "summary": "breve resumen en español",
  "covered_aspects": ["aspecto 1", "aspecto 2"],
  "missing_aspects": ["aspecto faltante 1", "aspecto faltante 2"],
  "evidence_quotes": ["cita 1", "cita 2"],
  "recommendations": ["recomendación 1", "recomendación 2"],
  "maturity_suggestion": 2-6
}}
"""
        return prompt

    def call_ai_api(self, prompt: str) -> Dict:
        """Llama a la API de IA según el proveedor configurado"""
        start_time = time.time()

        try:
            if self.provider == 'ollama':
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    },
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()

                # Parsear la respuesta JSON
                try:
                    analysis = json.loads(result['response'])
                except json.JSONDecodeError:
                    # Si no es JSON válido, intentar extraerlo
                    text = result['response']
                    start_idx = text.find('{')
                    end_idx = text.rfind('}') + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        analysis = json.loads(text[start_idx:end_idx])
                    else:
                        raise Exception("Respuesta no contiene JSON válido")

                return {
                    'analysis': analysis,
                    'tokens_used': result.get('eval_count', 0),
                    'time_taken': time.time() - start_time
                }

            elif self.provider == 'openai':
                from openai import OpenAI
                client = OpenAI(api_key=self.api_key)

                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )

                analysis = json.loads(response.choices[0].message.content)

                return {
                    'analysis': analysis,
                    'tokens_used': response.usage.total_tokens,
                    'time_taken': time.time() - start_time
                }

            elif self.provider == 'deepseek':
                from openai import OpenAI
                client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url or "https://api.deepseek.com"
                )

                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )

                analysis = json.loads(response.choices[0].message.content)

                return {
                    'analysis': analysis,
                    'tokens_used': response.usage.total_tokens,
                    'time_taken': time.time() - start_time
                }

            else:
                raise Exception(f"Proveedor no soportado: {self.provider}")

        except Exception as e:
            raise Exception(f"Error al llamar a la API de IA: {str(e)}")

    def verify_document_against_control(
        self,
        document_text: str,
        control: Dict,
        iso_context: str
    ) -> Dict:
        """
        Verifica un documento contra un control SOA específico
        Returns: Diccionario con resultados del análisis
        """
        prompt = self.build_verification_prompt(document_text, control, iso_context)
        result = self.call_ai_api(prompt)

        analysis = result['analysis']

        # Validar y normalizar la respuesta
        return {
            'compliance_status': analysis.get('compliance_status', 'non_compliant'),
            'confidence_level': int(analysis.get('confidence_level', 3)),
            'overall_score': int(analysis.get('overall_score', 0)),
            'summary': analysis.get('summary', ''),
            'covered_aspects': analysis.get('covered_aspects', []),
            'missing_aspects': analysis.get('missing_aspects', []),
            'evidence_quotes': analysis.get('evidence_quotes', []),
            'recommendations': analysis.get('recommendations', []),
            'maturity_suggestion': int(analysis.get('maturity_suggestion', 2)),
            'tokens_used': result['tokens_used'],
            'validation_time': result['time_taken']
        }

    def verify_document(self, document, controls: List) -> Dict:
        """
        Verifica un documento completo contra todos sus controles relacionados

        Args:
            document: Objeto Document de SQLAlchemy
            controls: Lista de controles SOA relacionados

        Returns:
            Diccionario con resultados agregados
        """
        # Verificar disponibilidad
        available, message = self.is_available()
        if not available:
            raise Exception(message)

        # Extraer texto del documento
        if not document.file_path or not os.path.exists(document.file_path):
            raise Exception("El documento no tiene un archivo válido")

        document_text = self.extract_text_from_document(document.file_path)

        if not document_text or len(document_text) < 100:
            raise Exception("El documento no contiene suficiente texto para analizar")

        # Cargar contexto ISO
        iso_context = self.load_knowledge_base()

        # Verificar contra cada control
        validations = []
        total_score = 0

        for control in controls:
            control_dict = {
                'control_id': control.control_id,
                'title': control.title,
                'description': control.description or '',
                'category': control.category
            }

            try:
                validation_result = self.verify_document_against_control(
                    document_text,
                    control_dict,
                    iso_context
                )
                validation_result['control_id'] = control.id
                validations.append(validation_result)
                total_score += validation_result['overall_score']

            except Exception as e:
                current_app.logger.error(f"Error verificando control {control.control_id}: {str(e)}")
                # Continuar con el siguiente control
                continue

        if not validations:
            raise Exception("No se pudo verificar ningún control")

        # Calcular score promedio
        avg_score = int(total_score / len(validations)) if validations else 0

        return {
            'overall_score': avg_score,
            'validations': validations,
            'total_controls': len(controls),
            'verified_controls': len(validations),
            'model_used': f"{self.provider}:{self.model}"
        }
