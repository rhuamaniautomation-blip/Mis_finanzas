# ============================================================
# GESTOR FINANCIERO PERSONAL - CAVA
# Diseñado por: CAVA - Especialistas en Robótica y Automatización
# Desarrollador: Roger Huamani
# Versión: 3.0 - Optimizada con caché y edición completa
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import hashlib
import os
from typing import List, Dict, Tuple, Optional, Any, Union
import json
import io
import csv
import time
from functools import lru_cache

# ============================================================
# CONFIGURACIÓN DE CONEXIÓN A SUPABASE
# ============================================================
SUPABASE_URL = "https://fpiwaophixldoouneanr.supabase.co"

try:
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

if not SUPABASE_KEY:
    st.error("⚠️ FALTA LA CLAVE DE SUPABASE\n\nConfigura SUPABASE_KEY en .streamlit/secrets.toml")
    st.stop()


# ============================================================
# CONFIGURACIÓN DE PÁGINA (DEBE IR PRIMERO)
# ============================================================
st.set_page_config(
    page_title="Gestor Financiero Personal - CAVA",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# IMPORTAR SUPABASE DESPUÉS DE SET_PAGE_CONFIG
# ============================================================
from supabase import create_client, Client


# ============================================================
# CACHÉ DE RECURSOS - OPTIMIZACIÓN DE RENDIMIENTO
# ============================================================
@st.cache_resource
def get_supabase_client() -> Client:
    """Cliente de Supabase cacheado - se reutiliza entre sesiones"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# ============================================================
# CSS PERSONALIZADO - RESPONSIVE Y ACCESIBLE
# ============================================================
st.markdown("""
<style>
:root {
    --color-primary: #d91e18;
    --color-success: #198754;
    --color-warning: #ffc107;
    --color-danger: #dc3545;
    --color-info: #0dcaf0;
    --color-bg-light: #f8f9fa;
    --color-bg-card: #ffffff;
    --color-text-primary: #212529;
    --color-text-secondary: #6c757d;
    --color-border: #dee2e6;
    --color-accent: #d4af37;
}

html, body {
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
    overflow-x: hidden;
}

.stApp {
    width: 100%;
    max-width: 100vw;
    margin: 0 auto;
    padding: 0;
    box-sizing: border-box;
}

.main .block-container {
    padding: 1.5rem 2rem;
    max-width: 100%;
    width: 100%;
    box-sizing: border-box;
}

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, sans-serif;
    color: var(--color-text-primary);
    line-height: 1.6;
    font-size: 16px;
}

h1 {
    font-size: clamp(1.5rem, 3vw, 2.25rem) !important;
    font-weight: 600 !important;
    color: var(--color-text-primary) !important;
    margin-bottom: 1rem !important;
    line-height: 1.3 !important;
}

h2 {
    font-size: clamp(1.25rem, 2.5vw, 1.75rem) !important;
    font-weight: 600 !important;
    color: var(--color-text-primary) !important;
    margin-top: 1.5rem !important;
}

h3 {
    font-size: clamp(1.1rem, 2vw, 1.35rem) !important;
    font-weight: 600 !important;
}

.metric-card {
    background-color: var(--color-bg-card);
    padding: clamp(0.75rem, 2vw, 1.5rem);
    border-radius: 12px;
    border: 1px solid var(--color-border);
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    margin: 0.5rem 0;
    transition: transform 0.2s, box-shadow 0.2s;
    width: 100%;
    box-sizing: border-box;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.saldo-card {
    background: linear-gradient(135deg, #198754 0%, #20c997 100%);
    color: white;
    padding: clamp(1rem, 3vw, 2rem);
    border-radius: 16px;
    margin: 1rem 0;
    box-shadow: 0 4px 12px rgba(25, 135, 84, 0.3);
    width: 100%;
    box-sizing: border-box;
}

.saldo-card.warning {
    background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
    box-shadow: 0 4px 12px rgba(255, 193, 7, 0.3);
}

.saldo-card.danger {
    background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
    box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
}

.saldo-amount {
    font-size: clamp(1.75rem, 5vw, 3rem);
    font-weight: 700;
    margin: 0.5rem 0;
    word-break: break-word;
}

.saldo-label {
    font-size: clamp(0.8rem, 1.5vw, 1rem);
    opacity: 0.95;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.paid-expense {
    background-color: #d1e7dd !important;
    padding: 0.75rem;
    border-radius: 8px;
    margin: 0.5rem 0;
}

.pending-expense {
    background-color: #fff3cd !important;
    padding: 0.75rem;
    border-radius: 8px;
    margin: 0.5rem 0;
}

.edit-card {
    background: linear-gradient(135deg, #fff3cd 0%, #ffe69c 100%);
    border: 2px solid #ffc107;
    padding: 1rem;
    border-radius: 12px;
    margin: 0.75rem 0;
    box-shadow: 0 2px 8px rgba(255, 193, 7, 0.2);
}

.footer-designer {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin-top: 2rem;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    border-top: 3px solid #d4af37;
}

.footer-designer h4 {
    color: #d4af37;
    margin: 0 0 0.5rem 0;
    font-size: clamp(0.9rem, 1.5vw, 1.1rem);
    font-weight: 600;
}

.footer-designer p {
    margin: 0.25rem 0;
    font-size: clamp(0.75rem, 1.2vw, 0.9rem);
    opacity: 0.95;
}

.footer-designer .brand {
    font-size: clamp(1rem, 1.8vw, 1.3rem);
    font-weight: 700;
    color: #d4af37;
    letter-spacing: 2px;
    margin-bottom: 0.5rem;
}

.footer-mini {
    background: #2c3e50;
    color: #d4af37;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    text-align: center;
    margin-top: 1rem;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 1px;
}

.goal-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.25rem;
    border-radius: 12px;
    margin: 0.5rem 0;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-edit {
    background-color: #ffc107 !important;
    color: #000 !important;
    border: none !important;
    font-weight: 600 !important;
}

.btn-edit:hover {
    background-color: #e0a800 !important;
}

.loading-spinner {
    text-align: center;
    padding: 2rem;
    color: var(--color-text-secondary);
}

@media (max-width: 768px) {
    .main .block-container { padding: 0.75rem; }
    h1 { font-size: 1.4rem !important; }
    h2 { font-size: 1.2rem !important; }
    .saldo-amount { font-size: 1.5rem; }
}

@media (min-width: 769px) and (max-width: 1024px) {
    .main .block-container { padding: 1rem; }
}

@media (min-width: 1921px) {
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1800px;
        margin: 0 auto;
    }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# GESTOR DE BASE DE DATOS (SUPABASE) - OPTIMIZADO
# ============================================================
class DatabaseManager:
    """Clase principal para gestionar todas las operaciones con Supabase"""

    def __init__(self):
        self.client = get_supabase_client()
        self._init_default_categories()

    def _init_default_categories(self):
        """Inicializa categorías por defecto si no existen"""
        try:
            response = self.client.table('categorias').select('id').limit(1).execute()
            if not response.data:
                categorias_default = [
                    {'nombre': 'Salario', 'tipo': 'ingreso', 'color': '#198754', 'icono': '💼'},
                    {'nombre': 'Freelance', 'tipo': 'ingreso', 'color': '#0dcaf0', 'icono': '💻'},
                    {'nombre': 'Ventas', 'tipo': 'ingreso', 'color': '#6f42c1', 'icono': '🛍️'},
                    {'nombre': 'Otros Ingresos', 'tipo': 'ingreso', 'color': '#20c997', 'icono': '💵'},
                    {'nombre': 'Vivienda', 'tipo': 'fijo', 'color': '#0d6efd', 'icono': '🏠'},
                    {'nombre': 'Alimentación', 'tipo': 'variable', 'color': '#fd7e14', 'icono': '🍔'},
                    {'nombre': 'Transporte', 'tipo': 'variable', 'color': '#198754', 'icono': '🚗'},
                    {'nombre': 'Servicios', 'tipo': 'fijo', 'color': '#dc3545', 'icono': '💡'},
                    {'nombre': 'Salud', 'tipo': 'variable', 'color': '#6f42c1', 'icono': '🏥'},
                    {'nombre': 'Educación', 'tipo': 'variable', 'color': '#795548', 'icono': '📚'},
                    {'nombre': 'Entretenimiento', 'tipo': 'variable', 'color': '#e83e8c', 'icono': '🎬'},
                    {'nombre': 'Ropa', 'tipo': 'variable', 'color': '#6c757d', 'icono': '👕'},
                    {'nombre': 'Seguros', 'tipo': 'fijo', 'color': '#ffc107', 'icono': '🛡️'},
                    {'nombre': 'Internet y Teléfono', 'tipo': 'fijo', 'color': '#0dcaf0', 'icono': '📱'},
                    {'nombre': 'Tarjetas de Crédito', 'tipo': 'fijo', 'color': '#fd7e14', 'icono': '💳'},
                    {'nombre': 'Impuestos SUNAT', 'tipo': 'fijo', 'color': '#6f42c1', 'icono': '📋'},
                    {'nombre': 'AFP/ONP', 'tipo': 'fijo', 'color': '#20c997', 'icono': '🏦'},
                    {'nombre': 'Otros', 'tipo': 'variable', 'color': '#495057', 'icono': '📦'}
                ]
                self.client.table('categorias').insert(categorias_default).execute()
        except Exception as e:
            pass

    # ==================== UTILIDADES DE CONVERSIÓN ====================
    @staticmethod
    def safe_float(value: Any, default: float = 0.0) -> float:
        """Convierte cualquier valor a float de forma segura"""
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def safe_int(value: Any, default: int = 0) -> int:
        """Convierte cualquier valor a int de forma segura"""
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def safe_str(value: Any, default: str = "") -> str:
        """Convierte cualquier valor a str de forma segura"""
        if value is None:
            return default
        return str(value)

    # ==================== USUARIOS ====================
    def crear_usuario(self, username: str, password: str, nombre_completo: str) -> bool:
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            self.client.table('usuarios').insert({
                'username': username,
                'password_hash': password_hash,
                'nombre_completo': nombre_completo
            }).execute()
            return True
        except Exception:
            return False

    def verificar_usuario(self, username: str, password: str) -> Optional[Dict]:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        response = self.client.table('usuarios').select(
            'id, username, nombre_completo'
        ).eq('username', username).eq('password_hash', password_hash).execute()
        if response.data:
            return {
                'id': response.data[0]['id'],
                'username': response.data[0]['username'],
                'nombre': response.data[0]['nombre_completo']
            }
        return None

    # ==================== CATEGORÍAS ====================
    def obtener_categorias(self, tipo: Optional[str] = None) -> List[Dict]:
        query = self.client.table('categorias').select('id, nombre, tipo, color, icono')
        if tipo:
            query = query.eq('tipo', tipo)
        response = query.execute()
        return response.data if response.data else []

    def agregar_categoria(self, nombre: str, tipo: str, color: str = '#607d8b',
                          icono: str = '📦') -> bool:
        try:
            self.client.table('categorias').insert({
                'nombre': nombre, 'tipo': tipo, 'color': color, 'icono': icono
            }).execute()
            return True
        except Exception:
            return False

    def eliminar_categoria(self, id: int) -> bool:
        try:
            self.client.table('categorias').delete().eq('id', id).execute()
            return True
        except Exception:
            return False

    # ==================== INGRESOS ====================
    def obtener_ingresos(self, activo: bool = True) -> List[Dict]:
        query = self.client.table('ingresos').select(
            'id, nombre, monto, categoria_id, fecha_pago, frecuencia, activo'
        )
        if activo:
            query = query.eq('activo', 1)
        query = query.order('fecha_pago', desc=False)
        response = query.execute()
        result = []
        for r in response.data:
            cat_response = self.client.table('categorias').select(
                'nombre, color, icono'
            ).eq('id', r['categoria_id']).execute()
            cat = cat_response.data[0] if cat_response.data else {
                'nombre': 'Sin categoría', 'color': '#607d8b', 'icono': '📦'
            }
            result.append({
                'id': r['id'],
                'nombre': self.safe_str(r['nombre']),
                'monto': self.safe_float(r['monto']),
                'categoria_id': self.safe_int(r['categoria_id']),
                'fecha_pago': self.safe_int(r['fecha_pago'], 1),
                'frecuencia': self.safe_str(r['frecuencia'], 'mensual'),
                'categoria_nombre': cat['nombre'],
                'color': cat['color'],
                'icono': cat['icono']
            })
        return result

    def obtener_ingreso_por_id(self, id: int) -> Optional[Dict]:
        """Obtiene un ingreso específico por su ID"""
        try:
            response = self.client.table('ingresos').select(
                'id, nombre, monto, categoria_id, fecha_pago, frecuencia, activo'
            ).eq('id', id).execute()
            if response.data:
                r = response.data[0]
                cat_response = self.client.table('categorias').select(
                    'nombre, color, icono'
                ).eq('id', r['categoria_id']).execute()
                cat = cat_response.data[0] if cat_response.data else {
                    'nombre': 'Sin categoría', 'color': '#607d8b', 'icono': '📦'
                }
                return {
                    'id': r['id'],
                    'nombre': self.safe_str(r['nombre']),
                    'monto': self.safe_float(r['monto']),
                    'categoria_id': self.safe_int(r['categoria_id']),
                    'fecha_pago': self.safe_int(r['fecha_pago'], 1),
                    'frecuencia': self.safe_str(r['frecuencia'], 'mensual'),
                    'categoria_nombre': cat['nombre'],
                    'color': cat['color'],
                    'icono': cat['icono']
                }
        except Exception:
            pass
        return None

    def agregar_ingreso(self, nombre: str, monto: float, categoria_id: int,
                        fecha_pago: int, frecuencia: str = 'mensual') -> int:
        try:
            response = self.client.table('ingresos').insert({
                'nombre': nombre,
                'monto': float(monto),
                'categoria_id': int(categoria_id),
                'fecha_pago': int(fecha_pago),
                'frecuencia': frecuencia,
                'activo': 1
            }).select('id').execute()
            return response.data[0]['id'] if response.data else 0
        except Exception as e:
            st.error(f"Error al agregar ingreso: {str(e)}")
            return 0

    def actualizar_ingreso(self, id: int, nombre: str, monto: float,
                           categoria_id: int, fecha_pago: int,
                           frecuencia: str) -> bool:
        try:
            self.client.table('ingresos').update({
                'nombre': nombre,
                'monto': float(monto),
                'categoria_id': int(categoria_id),
                'fecha_pago': int(fecha_pago),
                'frecuencia': frecuencia
            }).eq('id', int(id)).execute()
            return True
        except Exception as e:
            st.error(f"Error al actualizar ingreso: {str(e)}")
            return False

    def eliminar_ingreso(self, id: int) -> bool:
        try:
            response = self.client.table('ingresos').update(
                {'activo': 0}
            ).eq('id', int(id)).execute()
            return len(response.data) > 0
        except Exception:
            return False

    def crear_registro_ingreso_mensual(self, ingreso_id: int, mes: int,
                                       anio: int, monto: float) -> bool:
        try:
            self.client.table('ingresos_mensuales').insert({
                'ingreso_id': int(ingreso_id),
                'mes': int(mes),
                'anio': int(anio),
                'monto': float(monto),
                'recibido': 0
            }).execute()
            return True
        except Exception:
            return False

    def obtener_ingresos_mensuales(self, mes: int, anio: int) -> List[Dict]:
        response = self.client.table('ingresos_mensuales').select(
            'id, ingreso_id, monto, recibido, fecha_recibo_real, notas'
        ).eq('mes', int(mes)).eq('anio', int(anio)).execute()
        result = []
        for r in response.data:
            ing_response = self.client.table('ingresos').select(
                'nombre, fecha_pago, categoria_id'
            ).eq('id', r['ingreso_id']).execute()
            ing = ing_response.data[0] if ing_response.data else {
                'nombre': 'Sin nombre', 'fecha_pago': 1, 'categoria_id': None
            }
            cat_response = self.client.table('categorias').select(
                'nombre, color, icono'
            ).eq('id', ing['categoria_id']).execute() if ing['categoria_id'] else None
            cat = cat_response.data[0] if cat_response and cat_response.data else {
                'nombre': 'Sin categoría', 'color': '#607d8b', 'icono': '📦'
            }
            result.append({
                'id': r['id'],
                'ingreso_id': r['ingreso_id'],
                'monto': self.safe_float(r['monto']),
                'recibido': bool(r.get('recibido', 0)),
                'fecha_recibo_real': r.get('fecha_recibo_real'),
                'notas': self.safe_str(r.get('notas')),
                'nombre': self.safe_str(ing['nombre']),
                'fecha_pago': self.safe_int(ing['fecha_pago'], 1),
                'categoria_nombre': cat['nombre'],
                'color': cat['color'],
                'icono': cat['icono']
            })
        result.sort(key=lambda x: x['fecha_pago'] or 99)
        return result

    def marcar_ingreso_recibido(self, id: int, recibido: bool) -> bool:
        fecha_recibo = datetime.now().isoformat() if recibido else None
        response = self.client.table('ingresos_mensuales').update({
            'recibido': 1 if recibido else 0,
            'fecha_recibo_real': fecha_recibo
        }).eq('id', int(id)).execute()
        return len(response.data) > 0

    def actualizar_monto_ingreso_mensual(self, id: int, monto: float) -> bool:
        """Actualiza el monto de un ingreso mensual específico"""
        try:
            self.client.table('ingresos_mensuales').update({
                'monto': float(monto)
            }).eq('id', int(id)).execute()
            return True
        except Exception:
            return False

    def copiar_ingresos_a_mes(self, mes_origen: int, anio_origen: int,
                              mes_destino: int, anio_destino: int) -> int:
        response = self.client.table('ingresos_mensuales').select(
            'ingreso_id, monto'
        ).eq('mes', int(mes_origen)).eq('anio', int(anio_origen)).execute()
        copias = 0
        for r in response.data:
            try:
                self.client.table('ingresos_mensuales').insert({
                    'ingreso_id': r['ingreso_id'],
                    'mes': int(mes_destino),
                    'anio': int(anio_destino),
                    'monto': float(r['monto']),
                    'recibido': 0
                }).execute()
                copias += 1
            except Exception:
                pass
        return copias

    # ==================== GASTOS FIJOS ====================
    def obtener_gastos_fijos(self, activo: bool = True) -> List[Dict]:
        query = self.client.table('gastos_fijos').select(
            'id, nombre, monto, categoria_id, fecha_pago, frecuencia, activo'
        )
        if activo:
            query = query.eq('activo', 1)
        query = query.order('fecha_pago', desc=False)
        response = query.execute()
        result = []
        for r in response.data:
            cat_response = self.client.table('categorias').select(
                'nombre, color, icono'
            ).eq('id', r['categoria_id']).execute()
            cat = cat_response.data[0] if cat_response.data else {
                'nombre': 'Sin categoría', 'color': '#607d8b', 'icono': '📦'
            }
            result.append({
                'id': r['id'],
                'nombre': self.safe_str(r['nombre']),
                'monto': self.safe_float(r['monto']),
                'categoria_id': self.safe_int(r['categoria_id']),
                'fecha_pago': self.safe_int(r['fecha_pago'], 1),
                'frecuencia': self.safe_str(r['frecuencia'], 'mensual'),
                'categoria_nombre': cat['nombre'],
                'color': cat['color'],
                'icono': cat['icono']
            })
        return result

    def obtener_gasto_fijo_por_id(self, id: int) -> Optional[Dict]:
        """Obtiene un gasto fijo específico por su ID"""
        try:
            response = self.client.table('gastos_fijos').select(
                'id, nombre, monto, categoria_id, fecha_pago, frecuencia, activo'
            ).eq('id', id).execute()
            if response.data:
                r = response.data[0]
                cat_response = self.client.table('categorias').select(
                    'nombre, color, icono'
                ).eq('id', r['categoria_id']).execute()
                cat = cat_response.data[0] if cat_response.data else {
                    'nombre': 'Sin categoría', 'color': '#607d8b', 'icono': '📦'
                }
                return {
                    'id': r['id'],
                    'nombre': self.safe_str(r['nombre']),
                    'monto': self.safe_float(r['monto']),
                    'categoria_id': self.safe_int(r['categoria_id']),
                    'fecha_pago': self.safe_int(r['fecha_pago'], 1),
                    'frecuencia': self.safe_str(r['frecuencia'], 'mensual'),
                    'categoria_nombre': cat['nombre'],
                    'color': cat['color'],
                    'icono': cat['icono']
                }
        except Exception:
            pass
        return None

    def agregar_gasto_fijo(self, nombre: str, monto: float, categoria_id: int,
                           fecha_pago: int, frecuencia: str = 'mensual') -> int:
        try:
            response = self.client.table('gastos_fijos').insert({
                'nombre': nombre,
                'monto': float(monto),
                'categoria_id': int(categoria_id),
                'fecha_pago': int(fecha_pago),
                'frecuencia': frecuencia,
                'activo': 1
            }).select('id').execute()
            return response.data[0]['id'] if response.data else 0
        except Exception as e:
            st.error(f"Error al agregar gasto fijo: {str(e)}")
            return 0

    def actualizar_gasto_fijo(self, id: int, nombre: str, monto: float,
                              categoria_id: int, fecha_pago: int,
                              frecuencia: str) -> bool:
        try:
            self.client.table('gastos_fijos').update({
                'nombre': nombre,
                'monto': float(monto),
                'categoria_id': int(categoria_id),
                'fecha_pago': int(fecha_pago),
                'frecuencia': frecuencia
            }).eq('id', int(id)).execute()
            return True
        except Exception as e:
            st.error(f"Error al actualizar gasto fijo: {str(e)}")
            return False

    def eliminar_gasto_fijo(self, id: int) -> bool:
        try:
            response = self.client.table('gastos_fijos').update(
                {'activo': 0}
            ).eq('id', int(id)).execute()
            return len(response.data) > 0
        except Exception:
            return False

    def crear_registro_gasto_fijo_mensual(self, gasto_fijo_id: int, mes: int,
                                          anio: int, monto: float) -> bool:
        try:
            self.client.table('gastos_fijos_mensuales').insert({
                'gasto_fijo_id': int(gasto_fijo_id),
                'mes': int(mes),
                'anio': int(anio),
                'monto': float(monto),
                'pagado': 0
            }).execute()
            return True
        except Exception:
            return False

    def obtener_gastos_fijos_mensuales(self, mes: int, anio: int) -> List[Dict]:
        response = self.client.table('gastos_fijos_mensuales').select(
            'id, gasto_fijo_id, monto, pagado, fecha_pago_real, notas'
        ).eq('mes', int(mes)).eq('anio', int(anio)).execute()
        result = []
        for r in response.data:
            gf_response = self.client.table('gastos_fijos').select(
                'nombre, fecha_pago, categoria_id'
            ).eq('id', r['gasto_fijo_id']).execute()
            gf = gf_response.data[0] if gf_response.data else {
                'nombre': 'Sin nombre', 'fecha_pago': 1, 'categoria_id': None
            }
            cat_response = self.client.table('categorias').select(
                'nombre, color, icono'
            ).eq('id', gf['categoria_id']).execute() if gf['categoria_id'] else None
            cat = cat_response.data[0] if cat_response and cat_response.data else {
                'nombre': 'Sin categoría', 'color': '#607d8b', 'icono': '📦'
            }
            result.append({
                'id': r['id'],
                'gasto_fijo_id': r['gasto_fijo_id'],
                'monto': self.safe_float(r['monto']),
                'pagado': bool(r.get('pagado', 0)),
                'fecha_pago_real': r.get('fecha_pago_real'),
                'notas': self.safe_str(r.get('notas')),
                'nombre': self.safe_str(gf['nombre']),
                'fecha_pago': self.safe_int(gf['fecha_pago'], 1),
                'categoria_nombre': cat['nombre'],
                'color': cat['color'],
                'icono': cat['icono'],
                'categoria_id': self.safe_int(gf['categoria_id'])
            })
        result.sort(key=lambda x: x['fecha_pago'] or 99)
        return result

    def marcar_gasto_fijo_pagado(self, id: int, pagado: bool) -> bool:
        fecha_pago = datetime.now().isoformat() if pagado else None
        response = self.client.table('gastos_fijos_mensuales').update({
            'pagado': 1 if pagado else 0,
            'fecha_pago_real': fecha_pago
        }).eq('id', int(id)).execute()
        return len(response.data) > 0

    def actualizar_monto_gasto_fijo_mensual(self, id: int, monto: float) -> bool:
        """Actualiza el monto de un gasto fijo mensual específico"""
        try:
            self.client.table('gastos_fijos_mensuales').update({
                'monto': float(monto)
            }).eq('id', int(id)).execute()
            return True
        except Exception:
            return False

    def copiar_gastos_fijos_a_mes(self, mes_origen: int, anio_origen: int,
                                  mes_destino: int, anio_destino: int) -> int:
        response = self.client.table('gastos_fijos_mensuales').select(
            'gasto_fijo_id, monto'
        ).eq('mes', int(mes_origen)).eq('anio', int(anio_origen)).execute()
        copias = 0
        for r in response.data:
            try:
                self.client.table('gastos_fijos_mensuales').insert({
                    'gasto_fijo_id': r['gasto_fijo_id'],
                    'mes': int(mes_destino),
                    'anio': int(anio_destino),
                    'monto': float(r['monto']),
                    'pagado': 0
                }).execute()
                copias += 1
            except Exception:
                pass
        return copias

    # ==================== GASTOS VARIABLES ====================
    def obtener_gastos_variables(self, mes: Optional[int] = None,
                                 anio: Optional[int] = None) -> List[Dict]:
        query = self.client.table('gastos_variables').select(
            'id, descripcion, monto, categoria_id, fecha, mes, anio'
        )
        if mes and anio:
            query = query.eq('mes', int(mes)).eq('anio', int(anio))
        query = query.order('fecha', desc=True)
        response = query.execute()
        result = []
        for r in (response.data or []):
            cat_response = self.client.table('categorias').select(
                'nombre, color, icono'
            ).eq('id', r['categoria_id']).execute()
            cat = cat_response.data[0] if cat_response.data else {
                'nombre': 'Sin categoría', 'color': '#607d8b', 'icono': ''
            }
            result.append({
                'id': r['id'],
                'descripcion': self.safe_str(r['descripcion']),
                'monto': self.safe_float(r['monto']),
                'categoria_id': self.safe_int(r['categoria_id']),
                'fecha': self.safe_str(r['fecha']),
                'categoria_nombre': cat['nombre'],
                'color': cat['color'],
                'icono': cat['icono']
            })
        return result

    def obtener_gasto_variable_por_id(self, id: int) -> Optional[Dict]:
        """Obtiene un gasto variable específico por su ID"""
        try:
            response = self.client.table('gastos_variables').select(
                'id, descripcion, monto, categoria_id, fecha, mes, anio'
            ).eq('id', id).execute()
            if response.data:
                r = response.data[0]
                cat_response = self.client.table('categorias').select(
                    'nombre, color, icono'
                ).eq('id', r['categoria_id']).execute()
                cat = cat_response.data[0] if cat_response.data else {
                    'nombre': 'Sin categoría', 'color': '#607d8b', 'icono': ''
                }
                return {
                    'id': r['id'],
                    'descripcion': self.safe_str(r['descripcion']),
                    'monto': self.safe_float(r['monto']),
                    'categoria_id': self.safe_int(r['categoria_id']),
                    'fecha': self.safe_str(r['fecha']),
                    'categoria_nombre': cat['nombre'],
                    'color': cat['color'],
                    'icono': cat['icono']
                }
        except Exception:
            pass
        return None

    def agregar_gasto_variable(self, descripcion: str, monto: float,
                               categoria_id: int, fecha: str) -> int:
        try:
            fecha_dt = datetime.fromisoformat(fecha)
            response = self.client.table('gastos_variables').insert({
                'descripcion': descripcion,
                'monto': float(monto),
                'categoria_id': int(categoria_id),
                'fecha': fecha,
                'mes': fecha_dt.month,
                'anio': fecha_dt.year
            }).select('id').execute()
            return response.data[0]['id'] if response.data else 0
        except Exception as e:
            st.error(f"Error al agregar gasto variable: {str(e)}")
            return 0

    def actualizar_gasto_variable(self, id: int, descripcion: str, monto: float,
                                  categoria_id: int, fecha: str) -> bool:
        """Actualiza un gasto variable existente"""
        try:
            fecha_dt = datetime.fromisoformat(fecha)
            self.client.table('gastos_variables').update({
                'descripcion': descripcion,
                'monto': float(monto),
                'categoria_id': int(categoria_id),
                'fecha': fecha,
                'mes': fecha_dt.month,
                'anio': fecha_dt.year
            }).eq('id', int(id)).execute()
            return True
        except Exception as e:
            st.error(f"Error al actualizar gasto variable: {str(e)}")
            return False

    def eliminar_gasto_variable(self, id: int) -> bool:
        try:
            response = self.client.table('gastos_variables').delete().eq('id', int(id)).execute()
            return len(response.data) > 0
        except Exception:
            return False

    # ==================== PRÉSTAMOS ====================
    def obtener_prestamos(self, activo: bool = True) -> List[Dict]:
        query = self.client.table('prestamos').select(
            'id, nombre, monto_total, tasa_interes, fecha_inicio, fecha_fin, cuota_mensual, tipo, activo'
        )
        if activo:
            query = query.eq('activo', 1)
        query = query.order('fecha_inicio', desc=True)
        response = query.execute()
        result = []
        for r in (response.data or []):
            result.append({
                'id': r['id'],
                'nombre': self.safe_str(r['nombre']),
                'monto_total': self.safe_float(r['monto_total']),
                'tasa_interes': self.safe_float(r['tasa_interes']),
                'fecha_inicio': self.safe_str(r['fecha_inicio']),
                'fecha_fin': r.get('fecha_fin'),
                'cuota_mensual': self.safe_float(r['cuota_mensual']),
                'tipo': self.safe_str(r['tipo'], 'bancario'),
                'activo': bool(r.get('activo', 1))
            })
        return result

    def obtener_prestamo_por_id(self, id: int) -> Optional[Dict]:
        """Obtiene un préstamo específico por su ID"""
        try:
            response = self.client.table('prestamos').select(
                'id, nombre, monto_total, tasa_interes, fecha_inicio, fecha_fin, cuota_mensual, tipo, activo'
            ).eq('id', id).execute()
            if response.data:
                r = response.data[0]
                return {
                    'id': r['id'],
                    'nombre': self.safe_str(r['nombre']),
                    'monto_total': self.safe_float(r['monto_total']),
                    'tasa_interes': self.safe_float(r['tasa_interes']),
                    'fecha_inicio': self.safe_str(r['fecha_inicio']),
                    'fecha_fin': r.get('fecha_fin'),
                    'cuota_mensual': self.safe_float(r['cuota_mensual']),
                    'tipo': self.safe_str(r['tipo'], 'bancario'),
                    'activo': bool(r.get('activo', 1))
                }
        except Exception:
            pass
        return None

    def agregar_prestamo(self, nombre: str, monto_total: float, tasa_interes: float,
                         fecha_inicio: str, fecha_fin: Optional[str],
                         cuota_mensual: float, tipo: str = 'bancario') -> int:
        try:
            response = self.client.table('prestamos').insert({
                'nombre': nombre,
                'monto_total': float(monto_total),
                'tasa_interes': float(tasa_interes),
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'cuota_mensual': float(cuota_mensual),
                'tipo': tipo,
                'activo': 1
            }).select('id').execute()
            return response.data[0]['id'] if response.data else 0
        except Exception as e:
            st.error(f"Error al agregar préstamo: {str(e)}")
            return 0

    def actualizar_prestamo(self, id: int, nombre: str, monto_total: float,
                            tasa_interes: float, fecha_inicio: str,
                            fecha_fin: Optional[str], cuota_mensual: float,
                            tipo: str) -> bool:
        try:
            self.client.table('prestamos').update({
                'nombre': nombre,
                'monto_total': float(monto_total),
                'tasa_interes': float(tasa_interes),
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'cuota_mensual': float(cuota_mensual),
                'tipo': tipo
            }).eq('id', int(id)).execute()
            return True
        except Exception as e:
            st.error(f"Error al actualizar préstamo: {str(e)}")
            return False

    def eliminar_prestamo(self, id: int) -> bool:
        try:
            response = self.client.table('prestamos').update(
                {'activo': 0}
            ).eq('id', int(id)).execute()
            return len(response.data) > 0
        except Exception:
            return False

    def obtener_saldo_prestamo(self, prestamo_id: int) -> float:
        res_p = self.client.table('prestamos').select(
            'monto_total'
        ).eq('id', int(prestamo_id)).execute()
        if not res_p.data:
            return 0.0
        monto_total = self.safe_float(res_p.data[0]['monto_total'])
        res_pay = self.client.table('pagos_prestamos').select(
            'monto'
        ).eq('prestamo_id', int(prestamo_id)).execute()
        total_pagado = sum(self.safe_float(p['monto']) for p in (res_pay.data or []))
        return monto_total - total_pagado

    def obtener_pagos_prestamo_mes(self, prestamo_id: int, mes: int, anio: int) -> float:
        response = self.client.table('pagos_prestamos').select(
            'monto'
        ).eq('prestamo_id', int(prestamo_id)).eq('mes', int(mes)).eq('anio', int(anio)).execute()
        return sum(self.safe_float(p['monto']) for p in (response.data or []))

    def agregar_pago_prestamo(self, prestamo_id: int, monto: float,
                              fecha_pago: str) -> int:
        try:
            fecha_dt = datetime.fromisoformat(fecha_pago)
            response = self.client.table('pagos_prestamos').insert({
                'prestamo_id': int(prestamo_id),
                'monto': float(monto),
                'fecha_pago': fecha_pago,
                'mes': fecha_dt.month,
                'anio': fecha_dt.year
            }).select('id').execute()
            return response.data[0]['id'] if response.data else 0
        except Exception as e:
            st.error(f"Error al registrar pago: {str(e)}")
            return 0

    def actualizar_pago_prestamo(self, id: int, monto: float, fecha_pago: str,
                                 notas: str = "") -> bool:
        """Actualiza un pago de préstamo existente"""
        try:
            fecha_dt = datetime.fromisoformat(fecha_pago)
            self.client.table('pagos_prestamos').update({
                'monto': float(monto),
                'fecha_pago': fecha_pago,
                'mes': fecha_dt.month,
                'anio': fecha_dt.year,
                'notas': notas
            }).eq('id', int(id)).execute()
            return True
        except Exception as e:
            st.error(f"Error al actualizar pago: {str(e)}")
            return False

    def eliminar_pago_prestamo(self, id: int) -> bool:
        try:
            response = self.client.table('pagos_prestamos').delete().eq('id', int(id)).execute()
            return len(response.data) > 0
        except Exception:
            return False

    def obtener_historial_pagos_prestamo(self, prestamo_id: int) -> List[Dict]:
        response = self.client.table('pagos_prestamos').select(
            'id, monto, fecha_pago, mes, anio, notas'
        ).eq('prestamo_id', int(prestamo_id)).order('fecha_pago', desc=True).execute()
        result = []
        for r in (response.data or []):
            result.append({
                'id': r['id'],
                'monto': self.safe_float(r['monto']),
                'fecha_pago': self.safe_str(r['fecha_pago']),
                'mes': self.safe_int(r['mes']),
                'anio': self.safe_int(r['anio']),
                'notas': self.safe_str(r.get('notas'))
            })
        return result

    # ==================== AHORROS ====================
    def obtener_ahorros(self, mes: Optional[int] = None,
                        anio: Optional[int] = None) -> List[Dict]:
        query = self.client.table('ahorros').select(
            'id, concepto, monto, fecha, tipo, mes, anio'
        )
        if mes and anio:
            query = query.eq('mes', int(mes)).eq('anio', int(anio))
        query = query.order('fecha', desc=True)
        response = query.execute()
        result = []
        for r in (response.data or []):
            result.append({
                'id': r['id'],
                'concepto': self.safe_str(r['concepto']),
                'monto': self.safe_float(r['monto']),
                'fecha': self.safe_str(r['fecha']),
                'tipo': self.safe_str(r['tipo'], 'mensual'),
                'mes': self.safe_int(r['mes']),
                'anio': self.safe_int(r['anio'])
            })
        return result

    def obtener_ahorro_por_id(self, id: int) -> Optional[Dict]:
        """Obtiene un ahorro específico por su ID"""
        try:
            response = self.client.table('ahorros').select(
                'id, concepto, monto, fecha, tipo, mes, anio'
            ).eq('id', id).execute()
            if response.data:
                r = response.data[0]
                return {
                    'id': r['id'],
                    'concepto': self.safe_str(r['concepto']),
                    'monto': self.safe_float(r['monto']),
                    'fecha': self.safe_str(r['fecha']),
                    'tipo': self.safe_str(r['tipo'], 'mensual'),
                    'mes': self.safe_int(r['mes']),
                    'anio': self.safe_int(r['anio'])
                }
        except Exception:
            pass
        return None

    def agregar_ahorro(self, concepto: str, monto: float, fecha: str,
                       tipo: str = 'mensual') -> int:
        try:
            fecha_dt = datetime.fromisoformat(fecha)
            response = self.client.table('ahorros').insert({
                'concepto': concepto,
                'monto': float(monto),
                'fecha': fecha,
                'mes': fecha_dt.month,
                'anio': fecha_dt.year,
                'tipo': tipo
            }).select('id').execute()
            return response.data[0]['id'] if response.data else 0
        except Exception as e:
            st.error(f"Error al agregar ahorro: {str(e)}")
            return 0

    def actualizar_ahorro(self, id: int, concepto: str, monto: float,
                          fecha: str, tipo: str) -> bool:
        """Actualiza un ahorro existente"""
        try:
            fecha_dt = datetime.fromisoformat(fecha)
            self.client.table('ahorros').update({
                'concepto': concepto,
                'monto': float(monto),
                'fecha': fecha,
                'mes': fecha_dt.month,
                'anio': fecha_dt.year,
                'tipo': tipo
            }).eq('id', int(id)).execute()
            return True
        except Exception as e:
            st.error(f"Error al actualizar ahorro: {str(e)}")
            return False

    def eliminar_ahorro(self, id: int) -> bool:
        try:
            response = self.client.table('ahorros').delete().eq('id', int(id)).execute()
            return len(response.data) > 0
        except Exception:
            return False

    # ==================== PRESUPUESTOS ====================
    def obtener_presupuesto(self, categoria_id: int, mes: int, anio: int) -> Optional[float]:
        response = self.client.table('presupuestos').select(
            'monto'
        ).eq('categoria_id', int(categoria_id)).eq('mes', int(mes)).eq('anio', int(anio)).execute()
        return self.safe_float(response.data[0]['monto']) if response.data else None

    def establecer_presupuesto(self, categoria_id: int, mes: int, anio: int,
                               monto: float) -> bool:
        try:
            existing = self.client.table('presupuestos').select(
                'id'
            ).eq('categoria_id', int(categoria_id)).eq('mes', int(mes)).eq('anio', int(anio)).execute()
            if existing.data:
                self.client.table('presupuestos').update({
                    'monto': float(monto)
                }).eq('categoria_id', int(categoria_id)).eq('mes', int(mes)).eq('anio', int(anio)).execute()
            else:
                self.client.table('presupuestos').insert({
                    'categoria_id': int(categoria_id),
                    'mes': int(mes),
                    'anio': int(anio),
                    'monto': float(monto)
                }).execute()
            return True
        except Exception:
            return False

    def obtener_presupuestos_mes(self, mes: int, anio: int) -> List[Dict]:
        response = self.client.table('presupuestos').select(
            'id, categoria_id, monto'
        ).eq('mes', int(mes)).eq('anio', int(anio)).execute()
        result = []
        for r in (response.data or []):
            cat_response = self.client.table('categorias').select(
                'nombre, color, icono'
            ).eq('id', r['categoria_id']).execute()
            cat = cat_response.data[0] if cat_response.data else {
                'nombre': 'Sin categoría', 'color': '#607d8b', 'icono': '📦'
            }
            result.append({
                'id': r['id'],
                'categoria_id': r['categoria_id'],
                'monto': self.safe_float(r['monto']),
                'categoria_nombre': cat['nombre'],
                'color': cat['color'],
                'icono': cat['icono']
            })
        return result

    def eliminar_presupuesto(self, id: int) -> bool:
        """Elimina un presupuesto específico"""
        try:
            response = self.client.table('presupuestos').delete().eq('id', int(id)).execute()
            return len(response.data) > 0
        except Exception:
            return False

    # ==================== METAS FINANCIERAS ====================
    def obtener_metas(self, activo: bool = True) -> List[Dict]:
        query = self.client.table('metas_financieras').select(
            'id, nombre, monto_objetivo, monto_actual, fecha_limite, prioridad, descripcion, activo'
        )
        if activo:
            query = query.eq('activo', 1)
        query = query.order('fecha_limite', desc=False)
        response = query.execute()
        result = []
        for r in (response.data or []):
            result.append({
                'id': r['id'],
                'nombre': self.safe_str(r['nombre']),
                'monto_objetivo': self.safe_float(r['monto_objetivo']),
                'monto_actual': self.safe_float(r['monto_actual']),
                'fecha_limite': r.get('fecha_limite'),
                'prioridad': self.safe_str(r['prioridad'], 'media'),
                'descripcion': self.safe_str(r.get('descripcion')),
                'activo': bool(r.get('activo', 1))
            })
        return result

    def obtener_meta_por_id(self, id: int) -> Optional[Dict]:
        """Obtiene una meta específica por su ID"""
        try:
            response = self.client.table('metas_financieras').select(
                'id, nombre, monto_objetivo, monto_actual, fecha_limite, prioridad, descripcion, activo'
            ).eq('id', id).execute()
            if response.data:
                r = response.data[0]
                return {
                    'id': r['id'],
                    'nombre': self.safe_str(r['nombre']),
                    'monto_objetivo': self.safe_float(r['monto_objetivo']),
                    'monto_actual': self.safe_float(r['monto_actual']),
                    'fecha_limite': r.get('fecha_limite'),
                    'prioridad': self.safe_str(r['prioridad'], 'media'),
                    'descripcion': self.safe_str(r.get('descripcion')),
                    'activo': bool(r.get('activo', 1))
                }
        except Exception:
            pass
        return None

    def agregar_meta(self, nombre: str, monto_objetivo: float,
                     fecha_limite: Optional[str], prioridad: str = 'media',
                     descripcion: str = '') -> int:
        try:
            response = self.client.table('metas_financieras').insert({
                'nombre': nombre,
                'monto_objetivo': float(monto_objetivo),
                'fecha_limite': fecha_limite,
                'prioridad': prioridad,
                'descripcion': descripcion,
                'activo': 1
            }).select('id').execute()
            return response.data[0]['id'] if response.data else 0
        except Exception as e:
            st.error(f"Error al agregar meta: {str(e)}")
            return 0

    def actualizar_meta(self, id: int, nombre: str, monto_objetivo: float,
                        fecha_limite: Optional[str], prioridad: str,
                        descripcion: str) -> bool:
        """Actualiza una meta existente"""
        try:
            self.client.table('metas_financieras').update({
                'nombre': nombre,
                'monto_objetivo': float(monto_objetivo),
                'fecha_limite': fecha_limite,
                'prioridad': prioridad,
                'descripcion': descripcion
            }).eq('id', int(id)).execute()
            return True
        except Exception as e:
            st.error(f"Error al actualizar meta: {str(e)}")
            return False

    def agregar_aporte_meta(self, meta_id: int, monto: float, fecha: str,
                            notas: str = '') -> int:
        try:
            fecha_dt = datetime.fromisoformat(fecha)
            response = self.client.table('aportes_metas').insert({
                'meta_id': int(meta_id),
                'monto': float(monto),
                'fecha': fecha,
                'mes': fecha_dt.month,
                'anio': fecha_dt.year,
                'notas': notas
            }).select('id').execute()
            res_sum = self.client.table('aportes_metas').select(
                'monto'
            ).eq('meta_id', int(meta_id)).execute()
            total = sum(self.safe_float(a['monto']) for a in (res_sum.data or []))
            self.client.table('metas_financieras').update({
                'monto_actual': total
            }).eq('id', int(meta_id)).execute()
            return response.data[0]['id'] if response.data else 0
        except Exception as e:
            st.error(f"Error al registrar aporte: {str(e)}")
            return 0

    def obtener_aportes_meta_mes(self, meta_id: int, mes: int, anio: int) -> float:
        response = self.client.table('aportes_metas').select(
            'monto'
        ).eq('meta_id', int(meta_id)).eq('mes', int(mes)).eq('anio', int(anio)).execute()
        return sum(self.safe_float(a['monto']) for a in (response.data or []))

    def eliminar_meta(self, id: int) -> bool:
        try:
            response = self.client.table('metas_financieras').update(
                {'activo': 0}
            ).eq('id', int(id)).execute()
            return len(response.data) > 0
        except Exception:
            return False

    # ==================== EXPORTACIÓN ====================
    def exportar_a_csv(self, tabla: str, mes: int, anio: int) -> Optional[str]:
        try:
            if tabla == 'gastos_variables':
                response = self.client.table('gastos_variables').select(
                    '*'
                ).eq('mes', int(mes)).eq('anio', int(anio)).execute()
            elif tabla == 'gastos_fijos_mensuales':
                response = self.client.table('gastos_fijos_mensuales').select(
                    '*'
                ).eq('mes', int(mes)).eq('anio', int(anio)).execute()
            elif tabla == 'ingresos_mensuales':
                response = self.client.table('ingresos_mensuales').select(
                    '*'
                ).eq('mes', int(mes)).eq('anio', int(anio)).execute()
            else:
                return None
            if not response.data:
                return None
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(response.data[0].keys())
            for row in response.data:
                writer.writerow(row.values())
            return output.getvalue()
        except Exception:
            return None

    def obtener_todos_los_datos(self) -> Dict:
        datos = {}
        tablas = ['usuarios', 'categorias', 'ingresos', 'ingresos_mensuales',
                  'gastos_fijos', 'gastos_fijos_mensuales', 'gastos_variables',
                  'prestamos', 'pagos_prestamos', 'ahorros', 'presupuestos',
                  'metas_financieras', 'aportes_metas']
        for tabla in tablas:
            response = self.client.table(tabla).select('*').execute()
            datos[tabla] = response.data if response.data else []
        return datos


# ============================================================
# GESTOR DE ALERTAS
# ============================================================
class AlertManager:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def verificar_alertas(self, mes: int, anio: int) -> List[Dict]:
        alertas = []
        hoy = datetime.now()
        try:
            gastos_fijos = self.db.obtener_gastos_fijos_mensuales(mes, anio)
            for gasto in gastos_fijos:
                if not gasto['pagado']:
                    fecha_pago = gasto['fecha_pago']
                    if fecha_pago:
                        try:
                            fecha_pago_dt = datetime(anio, mes, int(fecha_pago))
                            dias_restantes = (fecha_pago_dt - hoy).days
                            if dias_restantes < 0:
                                alertas.append({
                                    'tipo': 'vencido',
                                    'mensaje': f"⚠️ {gasto['nombre']} está vencido ({abs(dias_restantes)} días)",
                                    'prioridad': 'alta'
                                })
                            elif dias_restantes <= 3:
                                alertas.append({
                                    'tipo': 'proximo',
                                    'mensaje': f"⏰ {gasto['nombre']} vence en {dias_restantes} días",
                                    'prioridad': 'media'
                                })
                        except ValueError:
                            pass
            saldo = calcular_saldo_disponible(self.db, mes, anio)
            ingresos = calcular_total_ingresos(self.db, mes, anio)
            if ingresos > 0:
                porcentaje_restante = (saldo / ingresos) * 100
                if saldo < 0:
                    alertas.append({
                        'tipo': 'saldo_negativo',
                        'mensaje': "🚨 ¡Saldo negativo! Estás gastando más de lo que ingresas",
                        'prioridad': 'critica'
                    })
                elif porcentaje_restante < 10:
                    alertas.append({
                        'tipo': 'saldo_bajo',
                        'mensaje': f"⚠️ Saldo bajo: solo te queda {porcentaje_restante:.1f}% de tus ingresos",
                        'prioridad': 'alta'
                    })
        except Exception as e:
            pass
        return alertas


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================
def formatear_moneda(monto: float) -> str:
    """Formatea un monto como moneda peruana"""
    try:
        return f"S/ {float(monto):,.2f}"
    except (ValueError, TypeError):
        return "S/ 0.00"


def calcular_total_ingresos(db: DatabaseManager, mes: int, anio: int) -> float:
    ingresos = db.obtener_ingresos_mensuales(mes, anio)
    return sum(float(i['monto']) for i in ingresos)


def calcular_total_gastos_fijos(db: DatabaseManager, mes: int, anio: int) -> float:
    gastos = db.obtener_gastos_fijos_mensuales(mes, anio)
    return sum(float(g['monto']) for g in gastos)


def calcular_total_gastos_variables(db: DatabaseManager, mes: int, anio: int) -> float:
    gastos = db.obtener_gastos_variables(mes, anio)
    return sum(float(g['monto']) for g in gastos)


def calcular_total_prestamos_mes(db: DatabaseManager, mes: int, anio: int) -> float:
    prestamos = db.obtener_prestamos()
    total = sum(db.obtener_pagos_prestamo_mes(p['id'], mes, anio) for p in prestamos)
    return total if total > 0 else sum(float(p['cuota_mensual']) for p in prestamos) if prestamos else 0.0


def calcular_total_ahorros_mes(db: DatabaseManager, mes: int, anio: int) -> float:
    ahorros = db.obtener_ahorros(mes, anio)
    return sum(float(a['monto']) for a in ahorros)


def calcular_total_aportes_metas_mes(db: DatabaseManager, mes: int, anio: int) -> float:
    metas = db.obtener_metas()
    return sum(db.obtener_aportes_meta_mes(m['id'], mes, anio) for m in metas)


def calcular_saldo_disponible(db: DatabaseManager, mes: int, anio: int) -> float:
    ingresos = calcular_total_ingresos(db, mes, anio)
    egresos = (calcular_total_gastos_fijos(db, mes, anio) +
               calcular_total_gastos_variables(db, mes, anio) +
               calcular_total_prestamos_mes(db, mes, anio) +
               calcular_total_ahorros_mes(db, mes, anio) +
               calcular_total_aportes_metas_mes(db, mes, anio))
    return ingresos - egresos


def obtener_meses_disponibles() -> List[Tuple[int, int, str]]:
    hoy = datetime.now()
    meses = []
    for i in range(-6, 7):
        fecha = hoy + relativedelta(months=i)
        meses.append((fecha.month, fecha.year, fecha.strftime('%B %Y')))
    return meses


def obtener_nombre_mes(mes: int, anio: int) -> str:
    meses_nombres = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    try:
        return f"{meses_nombres[int(mes)-1]} {int(anio)}"
    except (ValueError, IndexError):
        return f"Mes {mes} {anio}"


def render_saldo_card(db: DatabaseManager, mes: int, anio: int):
    saldo = calcular_saldo_disponible(db, mes, anio)
    ingresos = calcular_total_ingresos(db, mes, anio)
    if ingresos == 0:
        clase, mensaje = "", "⚠️ Registra tus ingresos para ver el saldo"
    elif saldo < 0:
        clase, mensaje = "danger", "🚨 Déficit: Estás gastando más de lo que ingresas"
    elif saldo < ingresos * 0.1:
        clase, mensaje = "warning", f"⚠️ Saldo bajo: {(saldo/ingresos)*100:.1f}% disponible"
    else:
        clase, mensaje = "", f"✅ Saludable: {(saldo/ingresos)*100:.1f}% disponible"
    st.markdown(f"""
    <div class="saldo-card {clase}">
        <div class="saldo-label">Saldo Disponible - {obtener_nombre_mes(mes, anio)}</div>
        <div class="saldo-amount">{formatear_moneda(saldo)}</div>
        <div style="font-size: 0.95rem; opacity: 0.95;">{mensaje}</div>
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    st.markdown("""
    <div class="footer-designer">
        <div class="brand">🤖 CAVA</div>
        <h4>Especialistas en Robótica y Automatización</h4>
        <p>Diseñado y desarrollado por <strong>Roger Huamani</strong></p>
        <p style="font-size: 0.8rem; opacity: 0.8; margin-top: 0.5rem;">
            © 2026 - Todos los derechos reservados
        </p>
    </div>
    """, unsafe_allow_html=True)


def safe_date_parse(fecha_str: Optional[str], default: Optional[date] = None) -> date:
    """Parsea una fecha de forma segura"""
    if default is None:
        default = datetime.now().date()
    if not fecha_str:
        return default
    try:
        # Intentar varios formatos
        for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f']:
            try:
                return datetime.strptime(fecha_str[:10], '%Y-%m-%d').date()
            except ValueError:
                continue
        return default
    except Exception:
        return default


# ============================================================
# SISTEMA DE AUTENTICACIÓN
# ============================================================
def login():
    st.title("🔐 Iniciar Sesión")
    st.markdown("### Gestor Financiero Personal - Perú 🇵🇪")
    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Ingresar")
        if submit:
            db = DatabaseManager()
            user = db.verificar_usuario(username, password)
            if user:
                st.session_state['logged_in'] = True
                st.session_state['user'] = user
                st.success("¡Inicio de sesión exitoso!")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")


def registro():
    st.title("📝 Registro de Usuario")
    st.markdown("### Crea tu cuenta para gestionar tus finanzas en Soles 🇵🇪")
    with st.form("registro_form"):
        nombre_completo = st.text_input("Nombre Completo")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        password_confirm = st.text_input("Confirmar Contraseña", type="password")
        submit = st.form_submit_button("Registrarse")
        if submit:
            if password != password_confirm:
                st.error("Las contraseñas no coinciden")
            elif len(password) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres")
            else:
                db = DatabaseManager()
                if db.crear_usuario(username, password, nombre_completo):
                    st.success("¡Registro exitoso! Ahora puedes iniciar sesión")
                    st.session_state['show_login'] = True
                else:
                    st.error("El nombre de usuario ya existe")


# ============================================================
# PÁGINA: INICIO (DASHBOARD)
# ============================================================
def pagina_inicio(db: DatabaseManager, mes: int, anio: int):
    st.title(f"📊 Dashboard - {obtener_nombre_mes(mes, anio)}")
    render_saldo_card(db, mes, anio)

    try:
        ingresos = db.obtener_ingresos_mensuales(mes, anio)
        gastos_fijos = db.obtener_gastos_fijos_mensuales(mes, anio)
        gastos_variables = db.obtener_gastos_variables(mes, anio)
        prestamos = db.obtener_prestamos()
        ahorros = db.obtener_ahorros(mes, anio)
        metas = db.obtener_metas()
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return

    total_ingresos = sum(float(i['monto']) for i in ingresos)
    total_ingresos_recibidos = sum(float(i['monto']) for i in ingresos if i['recibido'])
    total_gastos_fijos = sum(float(g['monto']) for g in gastos_fijos)
    total_gastos_fijos_pagados = sum(float(g['monto']) for g in gastos_fijos if g['pagado'])
    total_gastos_variables = sum(float(g['monto']) for g in gastos_variables)
    total_prestamos_mes = calcular_total_prestamos_mes(db, mes, anio)
    total_ahorros = sum(float(a['monto']) for a in ahorros)
    total_aportes_metas = calcular_total_aportes_metas_mes(db, mes, anio)
    total_egresos = (total_gastos_fijos + total_gastos_variables +
                     total_prestamos_mes + total_ahorros + total_aportes_metas)

    st.markdown("### 📈 Resumen del Mes")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #198754;">
            <div style="font-size: 0.85rem; color: #6c757d; text-transform: uppercase;">💵 Ingresos</div>
            <div style="font-size: 1.3rem; font-weight: 600; color: #198754;">{formatear_moneda(total_ingresos)}</div>
            <div style="font-size: 0.75rem; color: #6c757d;">Recibido: {formatear_moneda(total_ingresos_recibidos)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #dc3545;">
            <div style="font-size: 0.85rem; color: #6c757d; text-transform: uppercase;">💸 Egresos</div>
            <div style="font-size: 1.3rem; font-weight: 600; color: #dc3545;">{formatear_moneda(total_egresos)}</div>
            <div style="font-size: 0.75rem; color: #6c757d;">Fijos pagados: {formatear_moneda(total_gastos_fijos_pagados)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #0d6efd;">
            <div style="font-size: 0.85rem; color: #6c757d; text-transform: uppercase;">🏦 Ahorros</div>
            <div style="font-size: 1.3rem; font-weight: 600; color: #0d6efd;">{formatear_moneda(total_ahorros)}</div>
            <div style="font-size: 0.75rem; color: #6c757d;">Préstamos: {formatear_moneda(total_prestamos_mes)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #6f42c1;">
            <div style="font-size: 0.85rem; color: #6c757d; text-transform: uppercase;">🎯 Metas</div>
            <div style="font-size: 1.3rem; font-weight: 600; color: #6f42c1;">{formatear_moneda(total_aportes_metas)}</div>
            <div style="font-size: 0.75rem; color: #6c757d;">Aportado este mes</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        saldo = calcular_saldo_disponible(db, mes, anio)
        color_saldo = "#198754" if saldo >= 0 else "#dc3545"
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid {color_saldo};">
            <div style="font-size: 0.85rem; color: #6c757d; text-transform: uppercase;">💰 Saldo</div>
            <div style="font-size: 1.3rem; font-weight: 600; color: {color_saldo};">{formatear_moneda(saldo)}</div>
            <div style="font-size: 0.75rem; color: #6c757d;">Disponible</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    alert_manager = AlertManager(db)
    alertas = alert_manager.verificar_alertas(mes, anio)
    if alertas:
        st.subheader("🔔 Alertas")
        for alerta in alertas:
            if alerta['prioridad'] in ['critica', 'alta']:
                st.error(alerta['mensaje'])
            else:
                st.warning(alerta['mensaje'])
        st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Distribución del Ingreso")
        if total_ingresos > 0:
            saldo = calcular_saldo_disponible(db, mes, anio)
            data = pd.DataFrame([
                {'Concepto': 'Gastos Fijos', 'Monto': total_gastos_fijos},
                {'Concepto': 'Gastos Variables', 'Monto': total_gastos_variables},
                {'Concepto': 'Préstamos', 'Monto': total_prestamos_mes},
                {'Concepto': 'Ahorros', 'Monto': total_ahorros},
                {'Concepto': 'Metas', 'Monto': total_aportes_metas},
                {'Concepto': 'Disponible', 'Monto': max(saldo, 0)}
            ])
            data = data[data['Monto'] > 0]
            if not data.empty:
                fig = px.pie(data, values='Monto', names='Concepto', hole=0.4)
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("💡 Registra tus ingresos en '💵 Ingresos'")

    with col2:
        st.subheader("📉 Presupuesto vs Real")
        presupuestos = db.obtener_presupuestos_mes(mes, anio)
        if presupuestos:
            data_pres = []
            for pres in presupuestos:
                gasto_real = (
                    sum(float(g['monto']) for g in gastos_fijos if g['categoria_id'] == pres['categoria_id']) +
                    sum(float(g['monto']) for g in gastos_variables if g['categoria_id'] == pres['categoria_id'])
                )
                data_pres.append({
                    'Categoría': pres['categoria_nombre'],
                    'Presupuesto': float(pres['monto']),
                    'Real': gasto_real
                })
            df_pres = pd.DataFrame(data_pres)
            fig = go.Figure(data=[
                go.Bar(name='Presupuesto', x=df_pres['Categoría'],
                       y=df_pres['Presupuesto'], marker_color='#0d6efd'),
                go.Bar(name='Real', x=df_pres['Categoría'],
                       y=df_pres['Real'], marker_color='#fd7e14')
            ])
            fig.update_layout(barmode='group', height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Define presupuestos en '📊 Presupuestos'")

    if metas:
        st.markdown("---")
        st.subheader("🎯 Metas Financieras")
        cols = st.columns(min(len(metas), 3))
        for idx, meta in enumerate(metas[:6]):
            with cols[idx % len(cols)]:
                progreso = (float(meta['monto_actual']) / float(meta['monto_objetivo'])) * 100 if float(meta['monto_objetivo']) > 0 else 0
                st.markdown(f"""
                <div class="goal-card">
                    <div style="font-weight: 600; font-size: 1.1rem;">🎯 {meta['nombre']}</div>
                    <div style="font-size: 0.9rem; margin: 0.5rem 0;">
                        {formatear_moneda(meta['monto_actual'])} / {formatear_moneda(meta['monto_objetivo'])}
                    </div>
                    <div style="background: rgba(255,255,255,0.3); border-radius: 10px; height: 10px; overflow: hidden;">
                        <div style="background: white; height: 100%; width: {min(progreso, 100)}%;"></div>
                    </div>
                    <div style="font-size: 0.85rem; margin-top: 0.5rem;">{progreso:.1f}% completado</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📋 Desglose de Movimientos")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 💵 Ingresos del Mes")
        if ingresos:
            for ing in ingresos:
                estado = "✅" if ing['recibido'] else "⏳"
                st.markdown(f"""
                <div class="{'paid-expense' if ing['recibido'] else 'pending-expense'}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{estado} {ing['icono'] or ''} {ing['nombre']}</strong>
                            <div style="font-size: 0.85rem; color: #6c757d;">
                                {ing['categoria_nombre'] or 'Sin categoría'} · Día {ing['fecha_pago']}
                            </div>
                        </div>
                        <div style="font-weight: 600; color: #198754; font-size: 1.1rem;">
                            {formatear_moneda(ing['monto'])}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay ingresos registrados")

    with col2:
        st.markdown("#### 💸 Gastos Fijos del Mes")
        if gastos_fijos:
            for gasto in gastos_fijos:
                estado = "✅" if gasto['pagado'] else "⏳"
                st.markdown(f"""
                <div class="{'paid-expense' if gasto['pagado'] else 'pending-expense'}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{estado} {gasto['icono'] or ''} {gasto['nombre']}</strong>
                            <div style="font-size: 0.85rem; color: #6c757d;">
                                {gasto['categoria_nombre'] or 'Sin categoría'} · Día {gasto['fecha_pago']}
                            </div>
                        </div>
                        <div style="font-weight: 600; color: #dc3545; font-size: 1.1rem;">
                            {formatear_moneda(gasto['monto'])}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay gastos fijos registrados")

    render_footer()


# ============================================================
# PÁGINA: INGRESOS (CON EDICIÓN COMPLETA)
# ============================================================
def pagina_ingresos(db: DatabaseManager, mes: int, anio: int):
    st.title("💵 Gestión de Ingresos")
    tab1, tab2, tab3 = st.tabs(["📝 Ingresos del Mes", "⚙️ Configurar Ingresos", "📋 Copiar a Otro Mes"])

    with tab1:
        st.subheader(f"Ingresos - {obtener_nombre_mes(mes, anio)}")
        ingresos = db.obtener_ingresos_mensuales(mes, anio)
        if ingresos:
            total = sum(float(i['monto']) for i in ingresos)
            recibidos = sum(float(i['monto']) for i in ingresos if i['recibido'])
            pendientes = total - recibidos
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Ingresos", formatear_moneda(total))
            col2.metric("Recibidos", formatear_moneda(recibidos))
            col3.metric("Pendientes", formatear_moneda(pendientes))
            saldo = calcular_saldo_disponible(db, mes, anio)
            if saldo >= 0:
                st.success(f"💰 **Saldo disponible:** {formatear_moneda(saldo)}")
            else:
                st.error(f"🚨 **Déficit:** {formatear_moneda(abs(saldo))}")
            st.markdown("---")

            for ingreso in ingresos:
                col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 1, 1])
                with col1:
                    estado = "✅ Recibido" if ingreso['recibido'] else "⏳ Pendiente"
                    st.markdown(f"**{ingreso['icono'] or ''} {ingreso['nombre']}**")
                    st.caption(estado)
                with col2:
                    st.markdown(f"**{ingreso['categoria_nombre'] or 'Sin categoría'}**")
                    st.caption(f"Día de pago: {ingreso['fecha_pago']}")
                with col3:
                    if ingreso['fecha_recibo_real']:
                        try:
                            fecha_dt = datetime.fromisoformat(ingreso['fecha_recibo_real'])
                            st.caption(f"Recibido: {fecha_dt.strftime('%d/%m/%Y')}")
                        except Exception:
                            pass
                with col4:
                    st.markdown(f"**{formatear_moneda(ingreso['monto'])}**")
                with col5:
                    if st.button("✓" if not ingreso['recibido'] else "↺",
                                 key=f"toggle_ing_{ingreso['id']}"):
                        db.marcar_ingreso_recibido(ingreso['id'], not ingreso['recibido'])
                        st.rerun()
                with col6:
                    if st.button("✏️", key=f"edit_ing_m_{ingreso['id']}"):
                        st.session_state[f"edit_ing_m_{ingreso['id']}"] = True

                # Formulario de edición inline
                if st.session_state.get(f"edit_ing_m_{ingreso['id']}", False):
                    with st.container():
                        st.markdown("#### ✏️ Editar Monto del Ingreso")
                        with st.form(f"form_edit_ing_m_{ingreso['id']}"):
                            nuevo_monto = st.number_input(
                                "Nuevo monto (S/)",
                                min_value=0.0,
                                step=0.01,
                                value=float(ingreso['monto']),
                                format="%.2f"
                            )
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.form_submit_button("💾 Guardar"):
                                    if nuevo_monto > 0:
                                        if db.actualizar_monto_ingreso_mensual(ingreso['id'], nuevo_monto):
                                            st.success("¡Monto actualizado!")
                                            st.session_state[f"edit_ing_m_{ingreso['id']}"] = False
                                            st.rerun()
                                    else:
                                        st.error("El monto debe ser mayor a 0")
                            with col_btn2:
                                if st.form_submit_button("❌ Cancelar"):
                                    st.session_state[f"edit_ing_m_{ingreso['id']}"] = False
                                    st.rerun()
        else:
            st.info("No hay ingresos para este mes.")

    with tab2:
        st.subheader("Configurar Ingresos")
        with st.form("nuevo_ingreso"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre del ingreso")
                monto = st.number_input("Monto (S/)", min_value=0.0, step=0.01, format="%.2f")
                fecha_pago = st.number_input("Día de pago (1-31)", min_value=1, max_value=31, value=1)
            with col2:
                categorias = db.obtener_categorias('ingreso')
                if categorias:
                    categoria_options = {f"{c['icono']} {c['nombre']}": c['id'] for c in categorias}
                    categoria_nombre = st.selectbox("Categoría", list(categoria_options.keys()))
                    categoria_id = categoria_options[categoria_nombre]
                else:
                    categoria_id = None
                frecuencia = st.selectbox("Frecuencia", ["mensual", "quincenal", "anual"])
            submit = st.form_submit_button("Agregar Ingreso")
            if submit:
                if nombre and monto > 0 and categoria_id:
                    ingreso_id = db.agregar_ingreso(nombre, monto, categoria_id, int(fecha_pago), frecuencia)
                    if ingreso_id:
                        db.crear_registro_ingreso_mensual(ingreso_id, mes, anio, monto)
                        st.success("¡Ingreso agregado!")
                        st.rerun()

        st.markdown("---")
        st.subheader("Ingresos Configurados")
        ingresos_config = db.obtener_ingresos()
        if ingresos_config:
            for ingreso in ingresos_config:
                with st.expander(f"{ingreso['icono'] or ''} {ingreso['nombre']} - {formatear_moneda(ingreso['monto'])}"):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.markdown(f"**Categoría:** {ingreso['categoria_nombre']}")
                        st.markdown(f"**Día de pago:** {ingreso['fecha_pago']}")
                        st.markdown(f"**Frecuencia:** {ingreso['frecuencia']}")
                    with col2:
                        st.markdown(f"**Monto:** {formatear_moneda(ingreso['monto'])}")
                    with col3:
                        if st.button("🗑️", key=f"del_ing_{ingreso['id']}"):
                            db.eliminar_ingreso(ingreso['id'])
                            st.rerun()
                        if st.button("✏️ Editar", key=f"edit_ing_{ingreso['id']}"):
                            st.session_state[f"edit_ingreso_{ingreso['id']}"] = True

                    # Formulario de edición
                    if st.session_state.get(f"edit_ingreso_{ingreso['id']}", False):
                        st.markdown("#### ✏️ Editar Ingreso")
                        with st.form(f"form_edit_ing_{ingreso['id']}"):
                            e_nombre = st.text_input("Nombre", value=ingreso['nombre'])
                            e_monto = st.number_input("Monto (S/)",
                                                      min_value=0.0,
                                                      step=0.01,
                                                      value=float(ingreso['monto']),
                                                      format="%.2f")
                            e_fecha = st.number_input("Día de pago",
                                                      min_value=1,
                                                      max_value=31,
                                                      value=int(ingreso['fecha_pago']))
                            categorias = db.obtener_categorias('ingreso')
                            if categorias:
                                cat_opts = {f"{c['icono']} {c['nombre']}": c['id'] for c in categorias}
                                cat_idx = list(cat_opts.values()).index(ingreso['categoria_id']) if ingreso['categoria_id'] in cat_opts.values() else 0
                                e_cat_nombre = st.selectbox("Categoría", list(cat_opts.keys()), index=cat_idx)
                                e_cat_id = cat_opts[e_cat_nombre]
                            else:
                                e_cat_id = ingreso['categoria_id']
                            e_frec = st.selectbox("Frecuencia",
                                                  ["mensual", "quincenal", "anual"],
                                                  index=["mensual", "quincenal", "anual"].index(ingreso['frecuencia']) if ingreso['frecuencia'] in ["mensual", "quincenal", "anual"] else 0)
                            col_b1, col_b2 = st.columns(2)
                            with col_b1:
                                if st.form_submit_button("💾 Guardar"):
                                    if e_nombre and e_monto > 0 and e_cat_id:
                                        if db.actualizar_ingreso(ingreso['id'], e_nombre, e_monto, e_cat_id, int(e_fecha), e_frec):
                                            st.success("¡Ingreso actualizado!")
                                            st.session_state[f"edit_ingreso_{ingreso['id']}"] = False
                                            st.rerun()
                            with col_b2:
                                if st.form_submit_button("❌ Cancelar"):
                                    st.session_state[f"edit_ingreso_{ingreso['id']}"] = False
                                    st.rerun()
        else:
            st.info("No hay ingresos configurados")

    with tab3:
        st.subheader("Copiar Ingresos a Otro Mes")
        col1, col2 = st.columns(2)
        with col1:
            mes_origen = st.selectbox("Mes Origen", range(1, 13), index=mes-1, key="mes_orig")
            anio_origen = st.number_input("Año Origen", value=anio, key="anio_orig")
        with col2:
            mes_destino = st.selectbox("Mes Destino", range(1, 13), index=mes-1, key="mes_dest")
            anio_destino = st.number_input("Año Destino", value=anio, key="anio_dest")
        if st.button("📋 Copiar"):
            if mes_origen == mes_destino and anio_origen == anio_destino:
                st.error("Deben ser diferentes")
            else:
                copias = db.copiar_ingresos_a_mes(mes_origen, anio_origen, mes_destino, anio_destino)
                st.success(f"¡Se copiaron {copias} ingresos!")
                st.rerun()

    render_footer()


# ============================================================
# PÁGINA: GASTOS FIJOS (CON EDICIÓN COMPLETA)
# ============================================================
def pagina_gastos_fijos(db: DatabaseManager, mes: int, anio: int):
    st.title("💳 Gestión de Gastos Fijos")
    tab1, tab2, tab3 = st.tabs(["📝 Gastos del Mes", "⚙️ Configurar Gastos", "📋 Copiar a Otro Mes"])

    with tab1:
        st.subheader(f"Gastos Fijos - {obtener_nombre_mes(mes, anio)}")
        gastos_fijos = db.obtener_gastos_fijos_mensuales(mes, anio)
        if gastos_fijos:
            total = sum(float(g['monto']) for g in gastos_fijos)
            pagados = sum(float(g['monto']) for g in gastos_fijos if g['pagado'])
            col1, col2, col3 = st.columns(3)
            col1.metric("Total", formatear_moneda(total))
            col2.metric("Pagados", formatear_moneda(pagados))
            col3.metric("Pendientes", formatear_moneda(total - pagados))
            st.markdown("---")

            for gasto in gastos_fijos:
                col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 1, 2, 1, 1])
                with col1:
                    estado = "✅ Pagado" if gasto['pagado'] else "⏳ Pendiente"
                    st.markdown(f"**{gasto['icono'] or ''} {gasto['nombre']}**")
                    st.caption(estado)
                with col2:
                    st.markdown(f"**{gasto['categoria_nombre'] or 'Sin categoría'}**")
                    st.caption(f"Día: {gasto['fecha_pago']}")
                with col3:
                    if gasto['fecha_pago_real']:
                        try:
                            st.caption(f"Pagado: {datetime.fromisoformat(gasto['fecha_pago_real']).strftime('%d/%m/%Y')}")
                        except Exception:
                            pass
                with col4:
                    st.markdown(f"**{formatear_moneda(gasto['monto'])}**")
                with col5:
                    if st.button("✓" if not gasto['pagado'] else "↺",
                                 key=f"toggle_gf_{gasto['id']}"):
                        db.marcar_gasto_fijo_pagado(gasto['id'], not gasto['pagado'])
                        st.rerun()
                with col6:
                    if st.button("✏️", key=f"edit_gf_m_{gasto['id']}"):
                        st.session_state[f"edit_gf_m_{gasto['id']}"] = True

                # Formulario de edición inline
                if st.session_state.get(f"edit_gf_m_{gasto['id']}", False):
                    with st.container():
                        st.markdown("#### ✏️ Editar Monto del Gasto Fijo")
                        with st.form(f"form_edit_gf_m_{gasto['id']}"):
                            nuevo_monto = st.number_input(
                                "Nuevo monto (S/)",
                                min_value=0.0,
                                step=0.01,
                                value=float(gasto['monto']),
                                format="%.2f"
                            )
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.form_submit_button("💾 Guardar"):
                                    if nuevo_monto > 0:
                                        if db.actualizar_monto_gasto_fijo_mensual(gasto['id'], nuevo_monto):
                                            st.success("¡Monto actualizado!")
                                            st.session_state[f"edit_gf_m_{gasto['id']}"] = False
                                            st.rerun()
                                    else:
                                        st.error("El monto debe ser mayor a 0")
                            with col_btn2:
                                if st.form_submit_button("❌ Cancelar"):
                                    st.session_state[f"edit_gf_m_{gasto['id']}"] = False
                                    st.rerun()
        else:
            st.info("No hay gastos fijos para este mes.")

    with tab2:
        st.subheader("Configurar Gastos Fijos")
        with st.form("nuevo_gasto_fijo"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre del gasto")
                monto = st.number_input("Monto (S/)", min_value=0.0, step=0.01, format="%.2f")
                fecha_pago = st.number_input("Día de pago (1-31)", min_value=1, max_value=31, value=1)
            with col2:
                categorias = db.obtener_categorias('fijo')
                if categorias:
                    categoria_options = {f"{c['icono']} {c['nombre']}": c['id'] for c in categorias}
                    categoria_nombre = st.selectbox("Categoría", list(categoria_options.keys()))
                    categoria_id = categoria_options[categoria_nombre]
                else:
                    categoria_id = None
                frecuencia = st.selectbox("Frecuencia", ["mensual", "anual", "trimestral"])
            submit = st.form_submit_button("Agregar Gasto Fijo")
            if submit:
                if nombre and monto > 0 and categoria_id:
                    gasto_id = db.agregar_gasto_fijo(nombre, monto, categoria_id, int(fecha_pago), frecuencia)
                    if gasto_id:
                        db.crear_registro_gasto_fijo_mensual(gasto_id, mes, anio, monto)
                        st.success("¡Gasto fijo agregado!")
                        st.rerun()

        st.markdown("---")
        st.subheader("Gastos Fijos Configurados")
        gastos_fijos_config = db.obtener_gastos_fijos()
        if gastos_fijos_config:
            for gasto in gastos_fijos_config:
                with st.expander(f"{gasto['icono'] or ''} {gasto['nombre']} - {formatear_moneda(gasto['monto'])}"):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.markdown(f"**Categoría:** {gasto['categoria_nombre']}")
                        st.markdown(f"**Día de pago:** {gasto['fecha_pago']}")
                        st.markdown(f"**Frecuencia:** {gasto['frecuencia']}")
                    with col2:
                        st.markdown(f"**Monto:** {formatear_moneda(gasto['monto'])}")
                    with col3:
                        if st.button("🗑️", key=f"del_gf_{gasto['id']}"):
                            db.eliminar_gasto_fijo(gasto['id'])
                            st.rerun()
                        if st.button("✏️ Editar", key=f"edit_gf_{gasto['id']}"):
                            st.session_state[f"edit_gasto_fijo_{gasto['id']}"] = True

                    # Formulario de edición
                    if st.session_state.get(f"edit_gasto_fijo_{gasto['id']}", False):
                        st.markdown("#### ✏️ Editar Gasto Fijo")
                        with st.form(f"form_edit_gf_{gasto['id']}"):
                            e_nombre = st.text_input("Nombre", value=gasto['nombre'])
                            e_monto = st.number_input("Monto (S/)",
                                                      min_value=0.0,
                                                      step=0.01,
                                                      value=float(gasto['monto']),
                                                      format="%.2f")
                            e_fecha = st.number_input("Día de pago",
                                                      min_value=1,
                                                      max_value=31,
                                                      value=int(gasto['fecha_pago']))
                            categorias = db.obtener_categorias('fijo')
                            if categorias:
                                cat_opts = {f"{c['icono']} {c['nombre']}": c['id'] for c in categorias}
                                cat_idx = list(cat_opts.values()).index(gasto['categoria_id']) if gasto['categoria_id'] in cat_opts.values() else 0
                                e_cat_nombre = st.selectbox("Categoría", list(cat_opts.keys()), index=cat_idx)
                                e_cat_id = cat_opts[e_cat_nombre]
                            else:
                                e_cat_id = gasto['categoria_id']
                            e_frec = st.selectbox("Frecuencia",
                                                  ["mensual", "anual", "trimestral"],
                                                  index=["mensual", "anual", "trimestral"].index(gasto['frecuencia']) if gasto['frecuencia'] in ["mensual", "anual", "trimestral"] else 0)
                            col_b1, col_b2 = st.columns(2)
                            with col_b1:
                                if st.form_submit_button("💾 Guardar"):
                                    if e_nombre and e_monto > 0 and e_cat_id:
                                        if db.actualizar_gasto_fijo(gasto['id'], e_nombre, e_monto, e_cat_id, int(e_fecha), e_frec):
                                            st.success("¡Gasto actualizado!")
                                            st.session_state[f"edit_gasto_fijo_{gasto['id']}"] = False
                                            st.rerun()
                            with col_b2:
                                if st.form_submit_button("❌ Cancelar"):
                                    st.session_state[f"edit_gasto_fijo_{gasto['id']}"] = False
                                    st.rerun()
        else:
            st.info("No hay gastos fijos configurados")

    with tab3:
        st.subheader("Copiar Gastos Fijos a Otro Mes")
        col1, col2 = st.columns(2)
        with col1:
            mes_origen = st.selectbox("Mes Origen", range(1, 13), index=mes-1, key="mes_orig_gf")
            anio_origen = st.number_input("Año Origen", value=anio, key="anio_orig_gf")
        with col2:
            mes_destino = st.selectbox("Mes Destino", range(1, 13), index=mes-1, key="mes_dest_gf")
            anio_destino = st.number_input("Año Destino", value=anio, key="anio_dest_gf")
        if st.button("📋 Copiar"):
            if mes_origen == mes_destino and anio_origen == anio_destino:
                st.error("Deben ser diferentes")
            else:
                copias = db.copiar_gastos_fijos_a_mes(mes_origen, anio_origen, mes_destino, anio_destino)
                st.success(f"¡Se copiaron {copias} gastos fijos!")
                st.rerun()

    render_footer()


# ============================================================
# PÁGINA: GASTOS VARIABLES (CORREGIDO - CON EDICIÓN)
# ============================================================
def pagina_gastos_variables(db: DatabaseManager, mes: int, anio: int):
    st.title("🛒 Gestión de Gastos Variables")

    try:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader(f"Gastos Variables - {obtener_nombre_mes(mes, anio)}")
            gastos_variables = db.obtener_gastos_variables(mes, anio)

            if gastos_variables and len(gastos_variables) > 0:
                total = sum(float(g['monto']) for g in gastos_variables)
                st.metric("Total Gastos Variables", formatear_moneda(total))
                st.markdown("---")

                for gasto in gastos_variables:
                    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
                    with col1:
                        st.markdown(f"**{gasto['icono'] or ''} {gasto['descripcion']}**")
                        try:
                            fecha_dt = datetime.fromisoformat(gasto['fecha'])
                            st.caption(fecha_dt.strftime('%d/%m/%Y'))
                        except Exception:
                            st.caption(gasto['fecha'])
                    with col2:
                        st.markdown(f"**{gasto['categoria_nombre'] or 'Sin categoría'}**")
                    with col3:
                        st.markdown(f"**{formatear_moneda(gasto['monto'])}**")
                    with col4:
                        if st.button("✏️", key=f"edit_gv_{gasto['id']}"):
                            st.session_state[f"edit_gasto_var_{gasto['id']}"] = True
                    with col5:
                        if st.button("🗑️", key=f"del_gv_{gasto['id']}"):
                            db.eliminar_gasto_variable(gasto['id'])
                            st.rerun()

                    # Formulario de edición inline
                    if st.session_state.get(f"edit_gasto_var_{gasto['id']}", False):
                        with st.container():
                            st.markdown("#### ✏️ Editar Gasto Variable")
                            with st.form(f"form_edit_gv_{gasto['id']}"):
                                e_desc = st.text_input("Descripción", value=gasto['descripcion'])
                                e_monto = st.number_input("Monto (S/)",
                                                          min_value=0.0,
                                                          step=0.01,
                                                          value=float(gasto['monto']),
                                                          format="%.2f")
                                categorias = db.obtener_categorias('variable')
                                if categorias:
                                    cat_opts = {f"{c['icono']} {c['nombre']}": c['id'] for c in categorias}
                                    cat_idx = list(cat_opts.values()).index(gasto['categoria_id']) if gasto['categoria_id'] in cat_opts.values() else 0
                                    e_cat_nombre = st.selectbox("Categoría", list(cat_opts.keys()), index=cat_idx)
                                    e_cat_id = cat_opts[e_cat_nombre]
                                else:
                                    e_cat_id = gasto['categoria_id']
                                try:
                                    fecha_actual = datetime.fromisoformat(gasto['fecha']).date()
                                except Exception:
                                    fecha_actual = datetime.now().date()
                                e_fecha = st.date_input("Fecha", value=fecha_actual)
                                col_b1, col_b2 = st.columns(2)
                                with col_b1:
                                    if st.form_submit_button("💾 Guardar"):
                                        if e_desc and e_monto > 0 and e_cat_id:
                                            if db.actualizar_gasto_variable(gasto['id'], e_desc, e_monto, e_cat_id, e_fecha.isoformat()):
                                                st.success("¡Gasto actualizado!")
                                                st.session_state[f"edit_gasto_var_{gasto['id']}"] = False
                                                st.rerun()
                                with col_b2:
                                    if st.form_submit_button("❌ Cancelar"):
                                        st.session_state[f"edit_gasto_var_{gasto['id']}"] = False
                                        st.rerun()

                saldo = calcular_saldo_disponible(db, mes, anio)
                st.info(f"💰 Saldo restante: **{formatear_moneda(saldo)}**")
            else:
                st.info("No hay gastos variables registrados para este mes.")

        with col2:
            st.subheader("Agregar Gasto Variable")
            with st.form("nuevo_gasto_variable"):
                descripcion = st.text_input("Descripción")
                monto = st.number_input("Monto (S/)", min_value=0.0, step=0.01, format="%.2f")
                categorias = db.obtener_categorias('variable')
                if categorias:
                    categoria_options = {f"{c['icono']} {c['nombre']}": c['id'] for c in categorias}
                    categoria_nombre = st.selectbox("Categoría", list(categoria_options.keys()))
                    categoria_id = categoria_options[categoria_nombre]
                else:
                    categoria_id = None
                fecha = st.date_input("Fecha", value=datetime.now())
                submit = st.form_submit_button("Agregar Gasto")
                if submit:
                    if descripcion and monto > 0 and categoria_id:
                        db.agregar_gasto_variable(descripcion, monto, categoria_id, fecha.isoformat())
                        st.success("¡Gasto variable agregado!")
                        st.rerun()

        st.markdown("---")
        st.subheader("📊 Distribución por Categoría")
        if gastos_variables and len(gastos_variables) > 0:
            gastos_por_categoria = {}
            for gasto in gastos_variables:
                cat = gasto['categoria_nombre'] or 'Sin categoría'
                gastos_por_categoria[cat] = gastos_por_categoria.get(cat, 0) + float(gasto['monto'])
            df = pd.DataFrame([{'Categoría': k, 'Monto': v} for k, v in gastos_por_categoria.items()])
            fig = px.pie(df, values='Monto', names='Categoría', hole=0.4)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Agrega gastos variables para ver la distribución")

    except Exception as e:
        st.error(f"Error al cargar gastos variables: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

    render_footer()


# ============================================================
# PÁGINA: PRÉSTAMOS (CORREGIDO - StreamlitMixedNumericTypesError)
# ============================================================
def pagina_prestamos(db: DatabaseManager, mes: int, anio: int):
    st.title("💰 Gestión de Préstamos y Deudas")
    tab1, tab2 = st.tabs(["📋 Mis Préstamos", "➕ Agregar Préstamo"])

    with tab1:
        prestamos = db.obtener_prestamos()
        if prestamos:
            total_deuda = sum(db.obtener_saldo_prestamo(p['id']) for p in prestamos)
            total_cuota_mes = calcular_total_prestamos_mes(db, mes, anio)
            st.info(f"💡 Deuda total: **{formatear_moneda(total_deuda)}** · Cuota del mes: **{formatear_moneda(total_cuota_mes)}**")
            st.markdown("---")

            for prestamo in prestamos:
                with st.expander(f"💳 {prestamo['nombre']} - {formatear_moneda(prestamo['monto_total'])}"):
                    saldo = db.obtener_saldo_prestamo(prestamo['id'])
                    total_pagado = float(prestamo['monto_total']) - saldo
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Monto Original", formatear_moneda(prestamo['monto_total']))
                        st.metric("Total Pagado", formatear_moneda(total_pagado))
                    with col2:
                        st.metric("Saldo Pendiente", formatear_moneda(saldo))
                        st.metric("Cuota Mensual", formatear_moneda(prestamo['cuota_mensual']))
                    with col3:
                        st.metric("Tasa de Interés", f"{float(prestamo['tasa_interes']):.2f}%")
                        st.metric("Tipo", str(prestamo['tipo']).capitalize())

                    progreso = (total_pagado / float(prestamo['monto_total'])) * 100 if float(prestamo['monto_total']) > 0 else 0
                    st.progress(min(progreso / 100, 1.0))
                    st.caption(f"{progreso:.1f}% pagado")

                    # Botones de acción
                    st.markdown("---")
                    col_acciones = st.columns(4)
                    with col_acciones[0]:
                        if st.button("✏️ Editar", key=f"edit_p_{prestamo['id']}"):
                            st.session_state[f"edit_prestamo_{prestamo['id']}"] = True
                    with col_acciones[1]:
                        if st.button("🗑️ Eliminar", key=f"del_p_{prestamo['id']}"):
                            if st.session_state.get(f"confirm_del_p_{prestamo['id']}", False):
                                db.eliminar_prestamo(prestamo['id'])
                                st.success("¡Préstamo eliminado!")
                                st.rerun()
                            else:
                                st.session_state[f"confirm_del_p_{prestamo['id']}"] = True
                                st.warning("Haz clic nuevamente para confirmar la eliminación")

                    # Formulario de edición
                    if st.session_state.get(f"edit_prestamo_{prestamo['id']}", False):
                        st.markdown("### ✏️ Editar Préstamo")
                        with st.form(f"edit_form_{prestamo['id']}"):
                            col_e1, col_e2 = st.columns(2)
                            with col_e1:
                                edit_nombre = st.text_input("Nombre", value=prestamo['nombre'])
                                edit_monto = st.number_input(
                                    "Monto total (S/)",
                                    min_value=0.0,
                                    step=0.01,
                                    value=float(prestamo['monto_total']),
                                    format="%.2f"
                                )
                                edit_tasa = st.number_input(
                                    "Tasa (%)",
                                    min_value=0.0,
                                    step=0.1,
                                    value=float(prestamo['tasa_interes']),
                                    format="%.2f"
                                )
                            with col_e2:
                                edit_cuota = st.number_input(
                                    "Cuota mensual (S/)",
                                    min_value=0.0,
                                    step=0.01,
                                    value=float(prestamo['cuota_mensual']),
                                    format="%.2f"
                                )
                                fecha_inicio_dt = safe_date_parse(prestamo['fecha_inicio'])
                                edit_fecha_inicio = st.date_input("Fecha inicio", value=fecha_inicio_dt)
                                if prestamo['fecha_fin']:
                                    fecha_fin_dt = safe_date_parse(prestamo['fecha_fin'])
                                    edit_fecha_fin = st.date_input("Fecha fin (opcional)", value=fecha_fin_dt)
                                else:
                                    edit_fecha_fin = st.date_input("Fecha fin (opcional)", value=None)
                                tipos_prestamo = ["bancario", "personal", "tarjeta de crédito", "vehículo", "hipotecario", "otro"]
                                tipo_actual = prestamo['tipo'] if prestamo['tipo'] in tipos_prestamo else "bancario"
                                edit_tipo = st.selectbox("Tipo", tipos_prestamo, index=tipos_prestamo.index(tipo_actual))

                            col_btn = st.columns(2)
                            with col_btn[0]:
                                if st.form_submit_button("💾 Guardar Cambios"):
                                    if edit_nombre and edit_monto > 0:
                                        db.actualizar_prestamo(
                                            prestamo['id'], edit_nombre, edit_monto,
                                            edit_tasa, edit_fecha_inicio.isoformat(),
                                            edit_fecha_fin.isoformat() if edit_fecha_fin else None,
                                            edit_cuota, edit_tipo
                                        )
                                        st.success("¡Préstamo actualizado!")
                                        st.session_state[f"edit_prestamo_{prestamo['id']}"] = False
                                        st.rerun()
                            with col_btn[1]:
                                if st.form_submit_button("❌ Cancelar"):
                                    st.session_state[f"edit_prestamo_{prestamo['id']}"] = False
                                    st.rerun()

                    # Registrar pago
                    st.markdown("---")
                    st.markdown("### 💸 Registrar Pago")
                    col1, col2 = st.columns(2)
                    with col1:
                        with st.form(f"pago_{prestamo['id']}"):
                            # *** CORRECCIÓN CRÍTICA: Conversión explícita a float ***
                            cuota_value = float(prestamo['cuota_mensual']) if prestamo['cuota_mensual'] else 0.0
                            monto_pago = st.number_input(
                                "Monto del pago (S/)",
                                min_value=0.0,
                                max_value=float(prestamo['monto_total']),
                                step=0.01,
                                value=cuota_value,
                                format="%.2f"
                            )
                            fecha_pago = st.date_input("Fecha de pago", value=datetime.now())
                            notas = st.text_input("Notas (opcional)")
                            if st.form_submit_button("💸 Registrar Pago"):
                                if monto_pago > 0:
                                    db.agregar_pago_prestamo(prestamo['id'], monto_pago, fecha_pago.isoformat())
                                    st.success("¡Pago registrado!")
                                    st.rerun()

                    with col2:
                        st.markdown("### 📜 Historial de Pagos")
                        historial = db.obtener_historial_pagos_prestamo(prestamo['id'])
                        if historial:
                            for pago in historial[:5]:
                                col_h1, col_h2, col_h3 = st.columns([2, 2, 1])
                                with col_h1:
                                    st.markdown(f"**{formatear_moneda(pago['monto'])}**")
                                    st.caption(pago['fecha_pago'])
                                with col_h2:
                                    if pago.get('notas'):
                                        st.caption(pago['notas'])
                                with col_h3:
                                    if st.button("✏️", key=f"edit_pago_{pago['id']}"):
                                        st.session_state[f"edit_pago_{pago['id']}"] = True
                                    if st.button("🗑️", key=f"del_pago_{pago['id']}"):
                                        db.eliminar_pago_prestamo(pago['id'])
                                        st.rerun()

                                # Edición inline del pago
                                if st.session_state.get(f"edit_pago_{pago['id']}", False):
                                    with st.form(f"form_edit_pago_{pago['id']}"):
                                        e_monto = st.number_input(
                                            "Nuevo monto (S/)",
                                            min_value=0.0,
                                            step=0.01,
                                            value=float(pago['monto']),
                                            format="%.2f"
                                        )
                                        try:
                                            fecha_actual = datetime.fromisoformat(pago['fecha_pago']).date()
                                        except Exception:
                                            fecha_actual = datetime.now().date()
                                        e_fecha = st.date_input("Fecha", value=fecha_actual)
                                        e_notas = st.text_input("Notas", value=pago.get('notas', ''))
                                        col_b1, col_b2 = st.columns(2)
                                        with col_b1:
                                            if st.form_submit_button("💾 Guardar"):
                                                if e_monto > 0:
                                                    db.actualizar_pago_prestamo(pago['id'], e_monto, e_fecha.isoformat(), e_notas)
                                                    st.success("¡Pago actualizado!")
                                                    st.session_state[f"edit_pago_{pago['id']}"] = False
                                                    st.rerun()
                                        with col_b2:
                                            if st.form_submit_button("❌ Cancelar"):
                                                st.session_state[f"edit_pago_{pago['id']}"] = False
                                                st.rerun()
                        else:
                            st.info("No hay pagos registrados")
        else:
            st.info("No hay préstamos registrados")

    with tab2:
        st.subheader("Agregar Nuevo Préstamo")
        with st.form("nuevo_prestamo"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre del préstamo")
                monto_total = st.number_input("Monto total (S/)", min_value=0.0, step=0.01, format="%.2f")
                tasa_interes = st.number_input("Tasa de interés (%)", min_value=0.0, step=0.1, format="%.2f")
            with col2:
                cuota_mensual = st.number_input("Cuota mensual (S/)", min_value=0.0, step=0.01, format="%.2f")
                fecha_inicio = st.date_input("Fecha de inicio", value=datetime.now())
                fecha_fin = st.date_input("Fecha de fin (opcional)", value=None)
                tipo = st.selectbox("Tipo de préstamo",
                                    ["bancario", "personal", "tarjeta de crédito", "vehículo", "hipotecario", "otro"])
            submit = st.form_submit_button("Agregar Préstamo")
            if submit:
                if nombre and monto_total > 0:
                    db.agregar_prestamo(nombre, monto_total, tasa_interes,
                                        fecha_inicio.isoformat(),
                                        fecha_fin.isoformat() if fecha_fin else None,
                                        cuota_mensual, tipo)
                    st.success("¡Préstamo agregado exitosamente!")
                    st.rerun()
                else:
                    st.error("Por favor completa todos los campos correctamente")

    render_footer()


# ============================================================
# PÁGINA: AHORROS (CON EDICIÓN COMPLETA)
# ============================================================
def pagina_ahorros(db: DatabaseManager, mes: int, anio: int):
    st.title("🏦 Gestión de Ahorros")

    try:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader(f"Ahorros - {obtener_nombre_mes(mes, anio)}")
            ahorros = db.obtener_ahorros(mes, anio)

            if ahorros and len(ahorros) > 0:
                total_ahorrado = sum(float(a['monto']) for a in ahorros)
                st.metric("Total Ahorrado este Mes", formatear_moneda(total_ahorrado))
                saldo = calcular_saldo_disponible(db, mes, anio)
                st.info(f"💰 Saldo disponible después de ahorrar: **{formatear_moneda(saldo)}**")
                st.markdown("---")

                for ahorro in ahorros:
                    col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
                    with col1:
                        st.markdown(f"**💰 {ahorro['concepto']}**")
                        try:
                            fecha_dt = datetime.fromisoformat(ahorro['fecha'])
                            st.caption(fecha_dt.strftime('%d/%m/%Y'))
                        except Exception:
                            st.caption(ahorro['fecha'])
                    with col2:
                        st.markdown(f"**{formatear_moneda(ahorro['monto'])}**")
                        st.caption(f"Tipo: {ahorro['tipo']}")
                    with col3:
                        st.markdown("")
                    with col4:
                        if st.button("✏️", key=f"edit_ah_{ahorro['id']}"):
                            st.session_state[f"edit_ahorro_{ahorro['id']}"] = True
                    with col5:
                        if st.button("🗑️", key=f"del_ah_{ahorro['id']}"):
                            db.eliminar_ahorro(ahorro['id'])
                            st.rerun()

                    # Formulario de edición inline
                    if st.session_state.get(f"edit_ahorro_{ahorro['id']}", False):
                        with st.container():
                            st.markdown("#### ✏️ Editar Ahorro")
                            with st.form(f"form_edit_ah_{ahorro['id']}"):
                                e_concepto = st.text_input("Concepto", value=ahorro['concepto'])
                                e_monto = st.number_input(
                                    "Monto (S/)",
                                    min_value=0.0,
                                    step=0.01,
                                    value=float(ahorro['monto']),
                                    format="%.2f"
                                )
                                try:
                                    fecha_actual = datetime.fromisoformat(ahorro['fecha']).date()
                                except Exception:
                                    fecha_actual = datetime.now().date()
                                e_fecha = st.date_input("Fecha", value=fecha_actual)
                                tipos_ahorro = ["mensual", "emergencia", "vacaciones", "inversión", "otro"]
                                tipo_actual = ahorro['tipo'] if ahorro['tipo'] in tipos_ahorro else "mensual"
                                e_tipo = st.selectbox("Tipo", tipos_ahorro, index=tipos_ahorro.index(tipo_actual))
                                col_b1, col_b2 = st.columns(2)
                                with col_b1:
                                    if st.form_submit_button("💾 Guardar"):
                                        if e_concepto and e_monto > 0:
                                            if db.actualizar_ahorro(ahorro['id'], e_concepto, e_monto, e_fecha.isoformat(), e_tipo):
                                                st.success("¡Ahorro actualizado!")
                                                st.session_state[f"edit_ahorro_{ahorro['id']}"] = False
                                                st.rerun()
                                with col_b2:
                                    if st.form_submit_button("❌ Cancelar"):
                                        st.session_state[f"edit_ahorro_{ahorro['id']}"] = False
                                        st.rerun()
            else:
                st.info("No hay ahorros registrados para este mes")

        with col2:
            st.subheader("Registrar Ahorro")
            with st.form("nuevo_ahorro"):
                concepto = st.text_input("Concepto")
                monto = st.number_input("Monto (S/)", min_value=0.0, step=0.01, format="%.2f")
                fecha = st.date_input("Fecha", value=datetime.now())
                tipo = st.selectbox("Tipo", ["mensual", "emergencia", "vacaciones", "inversión", "otro"])
                submit = st.form_submit_button("Registrar Ahorro")
                if submit:
                    if concepto and monto > 0:
                        db.agregar_ahorro(concepto, monto, fecha.isoformat(), tipo)
                        st.success("¡Ahorro registrado!")
                        st.rerun()

        st.markdown("---")
        st.subheader("📊 Historial de Ahorros")
        hoy = datetime.now()
        datos_historial = []
        for i in range(6):
            fecha = hoy - relativedelta(months=i)
            ahorros_mes = db.obtener_ahorros(fecha.month, fecha.year)
            total = sum(float(a['monto']) for a in ahorros_mes)
            datos_historial.append({'Mes': fecha.strftime('%b %Y'), 'Ahorro': total})
        df_historial = pd.DataFrame(datos_historial[::-1])
        fig = px.bar(df_historial, x='Mes', y='Ahorro', title='Ahorros de los Últimos 6 Meses',
                     color_discrete_sequence=['#198754'])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error al cargar ahorros: {str(e)}")

    render_footer()


# ============================================================
# PÁGINA: METAS FINANCIERAS (CON EDICIÓN)
# ============================================================
def pagina_metas(db: DatabaseManager, mes: int, anio: int):
    st.title("🎯 Metas Financieras")
    st.markdown("Define y sigue tus objetivos financieros: vacaciones, emergencia, compras, etc.")
    tab1, tab2 = st.tabs(["🎯 Mis Metas", "➕ Nueva Meta"])

    with tab1:
        metas = db.obtener_metas()
        if metas:
            for meta in metas:
                with st.expander(f"🎯 {meta['nombre']} - {formatear_moneda(meta['monto_actual'])} / {formatear_moneda(meta['monto_objetivo'])}"):
                    progreso = (float(meta['monto_actual']) / float(meta['monto_objetivo'])) * 100 if float(meta['monto_objetivo']) > 0 else 0
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Objetivo", formatear_moneda(meta['monto_objetivo']))
                        st.metric("Actual", formatear_moneda(meta['monto_actual']))
                    with col2:
                        st.metric("Falta", formatear_moneda(float(meta['monto_objetivo']) - float(meta['monto_actual'])))
                        st.metric("Prioridad", str(meta['prioridad']).capitalize())
                    with col3:
                        if meta['fecha_limite']:
                            try:
                                fecha_limite = datetime.fromisoformat(meta['fecha_limite'])
                                dias = (fecha_limite - datetime.now()).days
                                st.metric("Días restantes", dias)
                            except Exception:
                                st.metric("Fecha límite", "Inválida")
                        else:
                            st.metric("Fecha límite", "Sin definir")
                        st.metric("Progreso", f"{progreso:.1f}%")

                    st.progress(min(progreso / 100, 1.0))
                    if meta.get('descripcion'):
                        st.info(meta['descripcion'])

                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("✏️ Editar Meta", key=f"edit_meta_{meta['id']}"):
                            st.session_state[f"edit_meta_{meta['id']}"] = True
                    with col2:
                        if st.button("🗑️ Eliminar Meta", key=f"del_meta_{meta['id']}"):
                            db.eliminar_meta(meta['id'])
                            st.rerun()

                    # Formulario de edición
                    if st.session_state.get(f"edit_meta_{meta['id']}", False):
                        st.markdown("#### ✏️ Editar Meta")
                        with st.form(f"form_edit_meta_{meta['id']}"):
                            e_nombre = st.text_input("Nombre", value=meta['nombre'])
                            e_objetivo = st.number_input(
                                "Monto objetivo (S/)",
                                min_value=0.0,
                                step=0.01,
                                value=float(meta['monto_objetivo']),
                                format="%.2f"
                            )
                            if meta['fecha_limite']:
                                try:
                                    fecha_actual = datetime.fromisoformat(meta['fecha_limite']).date()
                                except Exception:
                                    fecha_actual = None
                                e_fecha = st.date_input("Fecha límite", value=fecha_actual)
                            else:
                                e_fecha = st.date_input("Fecha límite", value=None)
                            prioridades = ["alta", "media", "baja"]
                            prioridad_actual = meta['prioridad'] if meta['prioridad'] in prioridades else "media"
                            e_prioridad = st.selectbox("Prioridad", prioridades, index=prioridades.index(prioridad_actual))
                            e_desc = st.text_area("Descripción", value=meta.get('descripcion', ''))
                            col_b1, col_b2 = st.columns(2)
                            with col_b1:
                                if st.form_submit_button("💾 Guardar"):
                                    if e_nombre and e_objetivo > 0:
                                        db.actualizar_meta(
                                            meta['id'], e_nombre, e_objetivo,
                                            e_fecha.isoformat() if e_fecha else None,
                                            e_prioridad, e_desc
                                        )
                                        st.success("¡Meta actualizada!")
                                        st.session_state[f"edit_meta_{meta['id']}"] = False
                                        st.rerun()
                            with col_b2:
                                if st.form_submit_button("❌ Cancelar"):
                                    st.session_state[f"edit_meta_{meta['id']}"] = False
                                    st.rerun()

                    # Aportar a la meta
                    st.markdown("---")
                    st.markdown("### 💵 Aportar a esta meta")
                    with st.form(f"aporte_{meta['id']}"):
                        col_a1, col_a2 = st.columns([2, 1])
                        with col_a1:
                            monto_aporte = st.number_input(
                                "Monto (S/)",
                                min_value=0.0,
                                step=0.01,
                                format="%.2f"
                            )
                            fecha_aporte = st.date_input("Fecha", value=datetime.now())
                            notas = st.text_input("Notas (opcional)")
                        with col_a2:
                            st.markdown("")
                            st.markdown("")
                            if st.form_submit_button("💰 Aportar"):
                                if monto_aporte > 0:
                                    db.agregar_aporte_meta(meta['id'], monto_aporte, fecha_aporte.isoformat(), notas)
                                    st.success("¡Aporte registrado!")
                                    st.rerun()
        else:
            st.info("No hay metas financieras. ¡Crea tu primera meta!")

    with tab2:
        st.subheader("Crear Nueva Meta")
        with st.form("nueva_meta"):
            nombre = st.text_input("Nombre de la meta (ej: Vacaciones, Fondo de emergencia)")
            monto_objetivo = st.number_input("Monto objetivo (S/)", min_value=0.0, step=0.01, format="%.2f")
            col1, col2 = st.columns(2)
            with col1:
                fecha_limite = st.date_input("Fecha límite (opcional)", value=None)
            with col2:
                prioridad = st.selectbox("Prioridad", ["alta", "media", "baja"])
            descripcion = st.text_area("Descripción (opcional)")
            submit = st.form_submit_button("Crear Meta")
            if submit:
                if nombre and monto_objetivo > 0:
                    fecha_str = fecha_limite.isoformat() if fecha_limite else None
                    db.agregar_meta(nombre, monto_objetivo, fecha_str, prioridad, descripcion)
                    st.success("¡Meta creada exitosamente!")
                    st.rerun()
                else:
                    st.error("Completa nombre y monto objetivo")

    render_footer()


# ============================================================
# PÁGINA: PRESUPUESTOS
# ============================================================
def pagina_presupuestos(db: DatabaseManager, mes: int, anio: int):
    st.title("📊 Gestión de Presupuestos")
    st.subheader(f"Presupuestos - {obtener_nombre_mes(mes, anio)}")
    total_ingresos = calcular_total_ingresos(db, mes, anio)

    if total_ingresos > 0:
        st.success(f"💵 **Ingresos del mes:** {formatear_moneda(total_ingresos)}")
        st.info(f"""
        **Regla 50/30/20 sugerida:**
        - 🏠 **Necesidades (50%):** {formatear_moneda(total_ingresos * 0.5)}
        - 🎯 **Deseos (30%):** {formatear_moneda(total_ingresos * 0.3)}
        - 💰 **Ahorro (20%):** {formatear_moneda(total_ingresos * 0.2)}
        """)
    else:
        st.warning("⚠️ Registra tus ingresos primero")

    st.markdown("---")
    presupuestos = db.obtener_presupuestos_mes(mes, anio)
    categorias = db.obtener_categorias()
    gastos_fijos = db.obtener_gastos_fijos_mensuales(mes, anio)
    gastos_variables = db.obtener_gastos_variables(mes, anio)
    total_presupuestado = sum(float(p['monto']) for p in presupuestos)

    if total_ingresos > 0 and total_presupuestado > 0:
        porcentaje_usado = (total_presupuestado / total_ingresos) * 100
        if porcentaje_usado > 100:
            st.error(f"🚨 Tu presupuesto ({formatear_moneda(total_presupuestado)}) excede tus ingresos")
        elif porcentaje_usado > 90:
            st.warning(f"⚠️ Estás presupuestando el {porcentaje_usado:.1f}% de tus ingresos")
        else:
            st.success(f"✅ Has presupuestado el {porcentaje_usado:.1f}% de tus ingresos")

    if presupuestos:
        st.markdown("### Presupuestos Actuales")
        for pres in presupuestos:
            gasto_real = (
                sum(float(g['monto']) for g in gastos_fijos if g['categoria_id'] == pres['categoria_id']) +
                sum(float(g['monto']) for g in gastos_variables if g['categoria_id'] == pres['categoria_id'])
            )
            diferencia = float(pres['monto']) - gasto_real
            porcentaje = (gasto_real / float(pres['monto']) * 100) if float(pres['monto']) > 0 else 0
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
            with col1:
                st.markdown(f"**{pres['icono']} {pres['categoria_nombre']}**")
            with col2:
                st.markdown(f"Presupuesto: **{formatear_moneda(pres['monto'])}**")
                st.markdown(f"Gastado: **{formatear_moneda(gasto_real)}**")
            with col3:
                if diferencia >= 0:
                    st.success(f"Disponible: {formatear_moneda(diferencia)}")
                else:
                    st.error(f"Excedido: {formatear_moneda(abs(diferencia))}")
                st.progress(min(porcentaje / 100, 1.0))
                st.caption(f"{porcentaje:.1f}% usado")
            with col4:
                if st.button("✏️", key=f"edit_pres_{pres['id']}"):
                    st.session_state['edit_presupuesto'] = pres
            with col5:
                if st.button("🗑️", key=f"del_pres_{pres['id']}"):
                    db.eliminar_presupuesto(pres['id'])
                    st.rerun()
            st.markdown("---")

    st.markdown("### Configurar Presupuesto")
    if 'edit_presupuesto' in st.session_state:
        pres_edit = st.session_state['edit_presupuesto']
        default_categoria = pres_edit['categoria_id']
        default_monto = float(pres_edit['monto'])
    else:
        default_categoria = None
        default_monto = 0.0

    with st.form("configurar_presupuesto"):
        col1, col2 = st.columns(2)
        with col1:
            categoria_options = {f"{c['icono']} {c['nombre']}": c['id'] for c in categorias if c['tipo'] in ['fijo', 'variable']}
            if categoria_options:
                if default_categoria and default_categoria in categoria_options.values():
                    idx = list(categoria_options.values()).index(default_categoria)
                else:
                    idx = 0
                categoria_nombre = st.selectbox(
                    "Categoría",
                    list(categoria_options.keys()),
                    index=idx
                )
                categoria_id = categoria_options[categoria_nombre]
            else:
                categoria_id = None
        with col2:
            monto_presupuesto = st.number_input(
                "Monto del presupuesto (S/)",
                min_value=0.0,
                step=0.01,
                value=default_monto,
                format="%.2f"
            )
        submit = st.form_submit_button("Guardar Presupuesto")
        if submit:
            if monto_presupuesto > 0 and categoria_id:
                db.establecer_presupuesto(categoria_id, mes, anio, monto_presupuesto)
                if 'edit_presupuesto' in st.session_state:
                    del st.session_state['edit_presupuesto']
                st.success("¡Presupuesto guardado!")
                st.rerun()
            else:
                st.error("Completa todos los campos")

    render_footer()


# ============================================================
# PÁGINA: HISTORIAL
# ============================================================
def pagina_historial(db: DatabaseManager):
    st.title("📅 Historial Financiero")
    col1, col2, col3 = st.columns(3)
    with col1:
        mes_inicio = st.selectbox("Mes inicio", range(1, 13), index=0)
        anio_inicio = st.number_input("Año inicio", value=datetime.now().year - 1)
    with col2:
        mes_fin = st.selectbox("Mes fin", range(1, 13), index=datetime.now().month - 1)
        anio_fin = st.number_input("Año fin", value=datetime.now().year)

    datos_historial = []
    try:
        fecha_actual = datetime(int(anio_inicio), int(mes_inicio), 1)
        fecha_fin_dt = datetime(int(anio_fin), int(mes_fin), 1)
        while fecha_actual <= fecha_fin_dt:
            mes = fecha_actual.month
            anio = fecha_actual.year
            total_ingresos = calcular_total_ingresos(db, mes, anio)
            gastos_fijos = db.obtener_gastos_fijos_mensuales(mes, anio)
            total_fijos = sum(float(g['monto']) for g in gastos_fijos)
            gastos_variables = db.obtener_gastos_variables(mes, anio)
            total_variables = sum(float(g['monto']) for g in gastos_variables)
            ahorros = db.obtener_ahorros(mes, anio)
            total_ahorros = sum(float(a['monto']) for a in ahorros)
            total_prestamos = calcular_total_prestamos_mes(db, mes, anio)
            total_metas = calcular_total_aportes_metas_mes(db, mes, anio)
            saldo = total_ingresos - (total_fijos + total_variables + total_ahorros + total_prestamos + total_metas)
            datos_historial.append({
                'Mes': fecha_actual.strftime('%b %Y'),
                'Ingresos': total_ingresos,
                'Gastos Fijos': total_fijos,
                'Gastos Variables': total_variables,
                'Préstamos': total_prestamos,
                'Ahorros': total_ahorros,
                'Metas': total_metas,
                'Saldo': saldo
            })
            fecha_actual += relativedelta(months=1)
    except Exception as e:
        st.error(f"Error al procesar historial: {str(e)}")

    if datos_historial:
        df_historial = pd.DataFrame(datos_historial)
        st.subheader("📈 Evolución Financiera")
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Ingresos', x=df_historial['Mes'],
                             y=df_historial['Ingresos'], marker_color='#198754'))
        fig.add_trace(go.Bar(name='Gastos Fijos', x=df_historial['Mes'],
                             y=df_historial['Gastos Fijos'], marker_color='#0d6efd'))
        fig.add_trace(go.Bar(name='Gastos Variables', x=df_historial['Mes'],
                             y=df_historial['Gastos Variables'], marker_color='#fd7e14'))
        fig.add_trace(go.Scatter(name='Saldo', x=df_historial['Mes'],
                                 y=df_historial['Saldo'], mode='lines+markers',
                                 line=dict(color='#dc3545', width=3), marker=dict(size=10)))
        fig.update_layout(barmode='stack', height=500, xaxis_tickangle=-45, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Detalle por Mes")
        st.dataframe(df_historial.style.format({
            'Ingresos': 'S/ {:,.2f}', 'Gastos Fijos': 'S/ {:,.2f}',
            'Gastos Variables': 'S/ {:,.2f}', 'Préstamos': 'S/ {:,.2f}',
            'Ahorros': 'S/ {:,.2f}', 'Metas': 'S/ {:,.2f}', 'Saldo': 'S/ {:,.2f}'
        }), use_container_width=True)

        st.subheader("📊 Estadísticas del Período")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_ing = df_historial['Ingresos'].sum()
            st.metric("Total Ingresos", formatear_moneda(total_ing))
        with col2:
            total_gastos = df_historial['Gastos Fijos'].sum() + df_historial['Gastos Variables'].sum()
            st.metric("Total Gastos", formatear_moneda(total_gastos))
        with col3:
            total_ah = df_historial['Ahorros'].sum()
            st.metric("Total Ahorros", formatear_moneda(total_ah))
        with col4:
            saldo_total = df_historial['Saldo'].sum()
            st.metric("Saldo Total", formatear_moneda(saldo_total))

        csv = df_historial.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar Historial a CSV",
            data=csv,
            file_name="historial_financiero.csv",
            mime="text/csv"
        )
    else:
        st.info("No hay datos en el período seleccionado")

    render_footer()


# ============================================================
# PÁGINA: CONFIGURACIÓN (CORREGIDA)
# ============================================================
def pagina_configuracion(db: DatabaseManager):
    st.title("⚙️ Configuración")
    tab1, tab2, tab3 = st.tabs(["📂 Categorías", "👤 Usuario", "💾 Backup"])

    with tab1:
        st.subheader("Gestión de Categorías")
        with st.form("nueva_categoria"):
            st.markdown("### Agregar Nueva Categoría")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                nombre_categoria = st.text_input("Nombre")
            with col2:
                tipo_categoria = st.selectbox("Tipo", ["ingreso", "fijo", "variable"])
            with col3:
                icono_categoria = st.text_input("Icono (emoji)", value="📦", max_chars=2)
            with col4:
                color_categoria = st.color_picker("Color", value="#607d8b")
            submit = st.form_submit_button("Agregar Categoría")
            if submit:
                if nombre_categoria:
                    if db.agregar_categoria(nombre_categoria, tipo_categoria, color_categoria, icono_categoria):
                        st.success("¡Categoría agregada!")
                        st.rerun()
                    else:
                        st.error("Error al agregar la categoría")

        st.markdown("---")
        st.subheader("Categorías Existentes")
        try:
            categorias = db.obtener_categorias()
            if categorias:
                for categoria in categorias:
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    with col1:
                        st.markdown(f"**{categoria['icono']} {categoria['nombre']}**")
                    with col2:
                        st.markdown(f"Tipo: **{categoria['tipo'].capitalize()}**")
                    with col3:
                        st.markdown(f"Color: {categoria['color']}")
                    with col4:
                        if st.button("🗑️", key=f"del_cat_{categoria['id']}"):
                            db.eliminar_categoria(categoria['id'])
                            st.rerun()
            else:
                st.info("No hay categorías registradas")
        except Exception as e:
            st.error(f"Error al cargar categorías: {str(e)}")

    with tab2:
        st.subheader("Información del Usuario")
        if 'user' in st.session_state:
            user = st.session_state['user']
            st.markdown(f"**Usuario:** {user['username']}")
            st.markdown(f"**Nombre:** {user['nombre']}")
            st.markdown(f"**ID:** {user['id']}")
            st.markdown("---")
            if st.button("🚪 Cerrar Sesión"):
                if 'logged_in' in st.session_state:
                    del st.session_state['logged_in']
                if 'user' in st.session_state:
                    del st.session_state['user']
                st.rerun()
        else:
            st.warning("No hay usuario logueado")

    with tab3:
        st.subheader("Backup y Restauración")
        st.info("💡 Realiza backups periódicos de tus datos financieros")
        if st.button("📥 Descargar Backup Completo (JSON)"):
            try:
                datos = db.obtener_todos_los_datos()
                backup = {
                    'fecha': datetime.now().isoformat(),
                    'version': '3.0',
                    'datos': datos
                }
                json_str = json.dumps(backup, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📥 Descargar Backup",
                    data=json_str,
                    file_name=f"backup_finanzas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                st.success("¡Backup generado!")
            except Exception as e:
                st.error(f"Error al generar backup: {str(e)}")

    render_footer()


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================
def main():
    """Función principal de la aplicación"""
    db = DatabaseManager()

    try:
        response = db.client.table('usuarios').select('id').limit(1).execute()
        hay_usuarios = len(response.data) > 0 if response.data else False
    except Exception:
        hay_usuarios = False

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        if not hay_usuarios:
            registro()
        else:
            if 'show_login' not in st.session_state:
                st.session_state['show_login'] = False
            if st.session_state['show_login']:
                login()
                if st.button("¿No tienes cuenta? Regístrate"):
                    st.session_state['show_login'] = False
                    st.rerun()
            else:
                login()
                if st.button("¿No tienes cuenta? Regístrate"):
                    st.session_state['show_login'] = True
                    st.rerun()
        return

    hoy = datetime.now()
    meses_disponibles = obtener_meses_disponibles()

    with st.sidebar:
        st.title("💰 Gestor Financiero")
        st.markdown(f"**Usuario:** {st.session_state['user']['nombre']}")
        st.markdown("---")
        st.subheader("📅 Período")
        mes_options = {f"{m[2]}": (m[0], m[1]) for m in meses_disponibles}
        mes_seleccionado = st.selectbox(
            "Seleccionar Mes",
            list(mes_options.keys()),
            index=6
        )
        mes, anio = mes_options[mes_seleccionado]
        saldo = calcular_saldo_disponible(db, mes, anio)
        color_saldo = "#198754" if saldo >= 0 else "#dc3545"
        st.markdown(f"""
        <div style="background: {color_saldo}; color: white; padding: 1rem; border-radius: 10px; margin: 1rem 0; text-align: center;">
            <div style="font-size: 0.8rem; opacity: 0.9;">SALDO DISPONIBLE</div>
            <div style="font-size: 1.5rem; font-weight: 700;">{formatear_moneda(saldo)}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("📋 Menú")
        pagina = st.radio(
            "Navegación",
            ["🏠 Inicio", "💵 Ingresos", "💳 Gastos Fijos", "🛒 Gastos Variables",
             "💰 Préstamos", "🏦 Ahorros", "🎯 Metas", "📊 Presupuestos",
             "📅 Historial", "⚙️ Configuración"],
            label_visibility="collapsed"
        )
        st.markdown("---")
        st.markdown("""
        <div class="footer-mini">
            🤖 CAVA - Roger Huamani
        </div>
        """, unsafe_allow_html=True)

    # Enrutamiento de páginas
    try:
        if pagina == "🏠 Inicio":
            pagina_inicio(db, mes, anio)
        elif pagina == "💵 Ingresos":
            pagina_ingresos(db, mes, anio)
        elif pagina == "💳 Gastos Fijos":
            pagina_gastos_fijos(db, mes, anio)
        elif pagina == "🛒 Gastos Variables":
            pagina_gastos_variables(db, mes, anio)
        elif pagina == "💰 Préstamos":
            pagina_prestamos(db, mes, anio)
        elif pagina == "🏦 Ahorros":
            pagina_ahorros(db, mes, anio)
        elif pagina == "🎯 Metas":
            pagina_metas(db, mes, anio)
        elif pagina == "📊 Presupuestos":
            pagina_presupuestos(db, mes, anio)
        elif pagina == "📅 Historial":
            pagina_historial(db)
        elif pagina == "⚙️ Configuración":
            pagina_configuracion(db)
    except Exception as e:
        st.error(f"Error al cargar la página: {str(e)}")
        import traceback
        st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
