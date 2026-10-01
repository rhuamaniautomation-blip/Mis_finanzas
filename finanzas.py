# ============================================================
# GESTOR FINANCIERO PERSONAL - CAVA
# Versión: 4.1 - Corregido y Optimizado
# Diseñado por: CAVA - Especialistas en Robótica y Automatización
# Desarrollador: Roger Huamani
# ============================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import hashlib
import os
from typing import List, Dict, Tuple, Optional, Any
import json
import io
import csv
from supabase import create_client, Client

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
# CONFIGURACIÓN DE PÁGINA
# ============================================================
st.set_page_config(
    page_title="Gestor Financiero Personal - CAVA",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# IMPORTAR SUPABASE
# ============================================================
@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = get_supabase_client()

# ============================================================
# CSS PERSONALIZADO
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
    --color-bg-card:  #ffffff;
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
}

h2 {
    font-size: clamp(1.25rem, 2.5vw, 1.75rem) !important;
    font-weight: 600 !important;
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

.saldo-card.info {
    background: linear-gradient(135deg, #0d6efd 0%, #0dcaf0 100%);
    box-shadow: 0 4px 12px rgba(13, 110, 253, 0.3);
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
# FUNCIONES AUXILIARES DE CONVERSIÓN
# ============================================================
def safe_float(value, default=0.0):
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_str(value, default=""):
    if value is None:
        return default
    return str(value)

# ============================================================
# GESTOR DE BASE DE DATOS (SUPABASE)
# ============================================================
class DatabaseManager:
    def __init__(self):
        self.client = supabase
        self._init_default_categories()

    def _init_default_categories(self):
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
        except Exception:
            pass

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

    def agregar_categoria(self, nombre: str, tipo: str, color: str = '#607d8b', icono: str = '📦') -> bool:
        try:
            self.client.table('categorias').insert({
                'nombre': nombre, 'tipo': tipo, 'color': color, 'icono': icono
            }).execute()
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
                'id': r['id'], 'nombre': safe_str(r['nombre']),
                'monto': safe_float(r['monto']),
                'categoria_id': safe_int(r['categoria_id']),
                'fecha_pago': safe_int(r['fecha_pago'], 1),
                'frecuencia': safe_str(r['frecuencia'], 'mensual'),
                'categoria_nombre': cat['nombre'],
                'color': cat['color'], 'icono': cat['icono']
            })
        return result

    def agregar_ingreso(self, nombre: str, monto: float, categoria_id: int,
                        fecha_pago: int, frecuencia: str = 'mensual') -> int:
        response = self.client.table('ingresos').insert({
            'nombre': nombre, 'monto': float(monto), 'categoria_id': int(categoria_id),
            'fecha_pago': int(fecha_pago), 'frecuencia': frecuencia, 'activo': 1
        }).select('id').execute()
        return response.data[0]['id'] if response.data else 0

    def eliminar_ingreso(self, id: int) -> bool:
        response = self.client.table('ingresos').update({'activo': 0}).eq('id', int(id)).execute()
        return len(response.data) > 0

    def crear_registro_ingreso_mensual(self, ingreso_id: int, mes: int,
                                       anio: int, monto: float) -> bool:
        try:
            self.client.table('ingresos_mensuales').insert({
                'ingreso_id': int(ingreso_id), 'mes': int(mes), 'anio': int(anio),
                'monto': float(monto), 'recibido': 0
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
                'id': r['id'], 'ingreso_id': r['ingreso_id'],
                'monto': safe_float(r['monto']),
                'recibido': bool(r.get('recibido', 0)),
                'fecha_recibo_real': r.get('fecha_recibo_real'),
                'notas': safe_str(r.get('notas')),
                'nombre': safe_str(ing['nombre']),
                'fecha_pago': safe_int(ing['fecha_pago'], 1),
                'categoria_nombre': cat['nombre'],
                'color': cat['color'], 'icono': cat['icono']
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

    def copiar_ingresos_a_mes(self, mes_origen: int, anio_origen: int,
                              mes_destino: int, anio_destino: int) -> int:
        response = self.client.table('ingresos_mensuales').select(
            'ingreso_id, monto'
        ).eq('mes', int(mes_origen)).eq('anio', int(anio_origen)).execute()
        copias = 0
        for r in response.data:
            try:
                self.client.table('ingresos_mensuales').insert({
                    'ingreso_id': r['ingreso_id'], 'mes': int(mes_destino),
                    'anio': int(anio_destino), 'monto': float(r['monto']), 'recibido': 0
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
                'id': r['id'], 'nombre': safe_str(r['nombre']),
                'monto': safe_float(r['monto']),
                'categoria_id': safe_int(r['categoria_id']),
                'fecha_pago': safe_int(r['fecha_pago'], 1),
                'frecuencia': safe_str(r['frecuencia'], 'mensual'),
                'categoria_nombre': cat['nombre'],
                'color': cat['color'], 'icono': cat['icono']
            })
        return result

    def agregar_gasto_fijo(self, nombre: str, monto: float, categoria_id: int,
                           fecha_pago: int, frecuencia: str = 'mensual') -> int:
        response = self.client.table('gastos_fijos').insert({
            'nombre': nombre, 'monto': float(monto), 'categoria_id': int(categoria_id),
            'fecha_pago': int(fecha_pago), 'frecuencia': frecuencia, 'activo': 1
        }).select('id').execute()
        return response.data[0]['id'] if response.data else 0

    def eliminar_gasto_fijo(self, id: int) -> bool:
        response = self.client.table('gastos_fijos').update({'activo': 0}).eq('id', int(id)).execute()
        return len(response.data) > 0

    def crear_registro_gasto_fijo_mensual(self, gasto_fijo_id: int, mes: int,
                                          anio: int, monto: float) -> bool:
        try:
            self.client.table('gastos_fijos_mensuales').insert({
                'gasto_fijo_id': int(gasto_fijo_id), 'mes': int(mes), 'anio': int(anio),
                'monto': float(monto), 'pagado': 0
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
                'id': r['id'], 'gasto_fijo_id': r['gasto_fijo_id'],
                'monto': safe_float(r['monto']),
                'pagado': bool(r.get('pagado', 0)),
                'fecha_pago_real': r.get('fecha_pago_real'),
                'notas': safe_str(r.get('notas')),
                'nombre': safe_str(gf['nombre']),
                'fecha_pago': safe_int(gf['fecha_pago'], 1),
                'categoria_nombre': cat['nombre'],
                'color': cat['color'], 'icono': cat['icono'],
                'categoria_id': safe_int(gf['categoria_id'])
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

    def copiar_gastos_fijos_a_mes(self, mes_origen: int, anio_origen: int,
                                  mes_destino: int, anio_destino: int) -> int:
        response = self.client.table('gastos_fijos_mensuales').select(
            'gasto_fijo_id, monto'
        ).eq('mes', int(mes_origen)).eq('anio', int(anio_origen)).execute()
        copias = 0
        for r in response.data:
            try:
                self.client.table('gastos_fijos_mensuales').insert({
                    'gasto_fijo_id': r['gasto_fijo_id'], 'mes': int(mes_destino),
                    'anio': int(anio_destino), 'monto': float(r['monto']), 'pagado': 0
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
                'nombre': 'Sin categoría', 'color': '#607d8b', 'icono': '📦'
            }
            result.append({
                'id': r['id'], 'descripcion': safe_str(r['descripcion']),
                'monto': safe_float(r['monto']),
                'categoria_id': safe_int(r['categoria_id']),
                'fecha': safe_str(r['fecha']),
                'categoria_nombre': cat['nombre'],
                'color': cat['color'], 'icono': cat['icono']
            })
        return result

    def agregar_gasto_variable(self, descripcion: str, monto: float,
                               categoria_id: int, fecha: str) -> int:
        fecha_dt = datetime.fromisoformat(fecha)
        response = self.client.table('gastos_variables').insert({
            'descripcion': descripcion, 'monto': float(monto),
            'categoria_id': int(categoria_id), 'fecha': fecha,
            'mes': fecha_dt.month, 'anio': fecha_dt.year
        }).select('id').execute()
        return response.data[0]['id'] if response.data else 0

    def eliminar_gasto_variable(self, id: int) -> bool:
        response = self.client.table('gastos_variables').delete().eq('id', int(id)).execute()
        return len(response.data) > 0

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
                'id': r['id'], 'nombre': safe_str(r['nombre']),
                'monto_total': safe_float(r['monto_total']),
                'tasa_interes': safe_float(r['tasa_interes']),
                'fecha_inicio': safe_str(r['fecha_inicio']),
                'fecha_fin': r.get('fecha_fin'),
                'cuota_mensual': safe_float(r['cuota_mensual']),
                'tipo': safe_str(r['tipo'], 'bancario'),
                'activo': bool(r.get('activo', 1))
            })
        return result

    def agregar_prestamo(self, nombre: str, monto_total: float, tasa_interes: float,
                         fecha_inicio: str, fecha_fin: Optional[str],
                         cuota_mensual: float, tipo: str = 'bancario') -> int:
        response = self.client.table('prestamos').insert({
            'nombre': nombre, 'monto_total': float(monto_total),
            'tasa_interes': float(tasa_interes), 'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin, 'cuota_mensual': float(cuota_mensual),
            'tipo': tipo, 'activo': 1
        }).select('id').execute()
        return response.data[0]['id'] if response.data else 0

    def eliminar_prestamo(self, id: int) -> bool:
        response = self.client.table('prestamos').update({'activo': 0}).eq('id', int(id)).execute()
        return len(response.data) > 0

    def obtener_saldo_prestamo(self, prestamo_id: int) -> float:
        res_p = self.client.table('prestamos').select('monto_total').eq('id', int(prestamo_id)).execute()
        if not res_p.data:
            return 0.0
        monto_total = safe_float(res_p.data[0]['monto_total'])
        res_pay = self.client.table('pagos_prestamos').select('monto').eq('prestamo_id', int(prestamo_id)).execute()
        total_pagado = sum(safe_float(p['monto']) for p in (res_pay.data or []))
        return monto_total - total_pagado

    def obtener_pagos_prestamo_mes(self, prestamo_id: int, mes: int, anio: int) -> float:
        response = self.client.table('pagos_prestamos').select('monto').eq('prestamo_id', int(prestamo_id)).eq('mes', int(mes)).eq('anio', int(anio)).execute()
        return sum(safe_float(p['monto']) for p in (response.data or []))

    def agregar_pago_prestamo(self, prestamo_id: int, monto: float, fecha_pago: str) -> int:
        fecha_dt = datetime.fromisoformat(fecha_pago)
        response = self.client.table('pagos_prestamos').insert({
            'prestamo_id': int(prestamo_id), 'monto': float(monto),
            'fecha_pago': fecha_pago, 'mes': fecha_dt.month, 'anio': fecha_dt.year
        }).select('id').execute()
        return response.data[0]['id'] if response.data else 0

    def obtener_historial_pagos_prestamo(self, prestamo_id: int) -> List[Dict]:
        response = self.client.table('pagos_prestamos').select(
            'id, monto, fecha_pago, mes, anio, notas'
        ).eq('prestamo_id', int(prestamo_id)).order('fecha_pago', desc=True).execute()
        result = []
        for r in (response.data or []):
            result.append({
                'id': r['id'], 'monto': safe_float(r['monto']),
                'fecha_pago': safe_str(r['fecha_pago']),
                'mes': safe_int(r['mes']), 'anio': safe_int(r['anio']),
                'notas': safe_str(r.get('notas'))
            })
        return result

    def eliminar_pago_prestamo(self, id: int) -> bool:
        response = self.client.table('pagos_prestamos').delete().eq('id', int(id)).execute()
        return len(response.data) > 0

    # ==================== AHORROS ====================
    def obtener_ahorros(self, mes: Optional[int] = None, anio: Optional[int] = None) -> List[Dict]:
        query = self.client.table('ahorros').select('id, concepto, monto, fecha, tipo, mes, anio')
        if mes and anio:
            query = query.eq('mes', int(mes)).eq('anio', int(anio))
        query = query.order('fecha', desc=True)
        response = query.execute()
        result = []
        for r in (response.data or []):
            result.append({
                'id': r['id'], 'concepto': safe_str(r['concepto']),
                'monto': safe_float(r['monto']), 'fecha': safe_str(r['fecha']),
                'tipo': safe_str(r['tipo'], 'mensual'),
                'mes': safe_int(r['mes']), 'anio': safe_int(r['anio'])
            })
        return result

    def agregar_ahorro(self, concepto: str, monto: float, fecha: str, tipo: str = 'mensual') -> int:
        fecha_dt = datetime.fromisoformat(fecha)
        response = self.client.table('ahorros').insert({
            'concepto': concepto, 'monto': float(monto), 'fecha': fecha,
            'mes': fecha_dt.month, 'anio': fecha_dt.year, 'tipo': tipo
        }).select('id').execute()
        return response.data[0]['id'] if response.data else 0

    def eliminar_ahorro(self, id: int) -> bool:
        response = self.client.table('ahorros').delete().eq('id', int(id)).execute()
        return len(response.data) > 0

    # ==================== PRESUPUESTOS ====================
    def obtener_presupuestos_mes(self, mes: int, anio: int) -> List[Dict]:
        response = self.client.table('presupuestos').select('id, categoria_id, monto').eq('mes', int(mes)).eq('anio', int(anio)).execute()
        result = []
        for r in (response.data or []):
            cat_response = self.client.table('categorias').select('nombre, color, icono').eq('id', r['categoria_id']).execute()
            cat = cat_response.data[0] if cat_response.data else {'nombre': 'Sin categoría', 'color': '#607d8b', 'icono': '📦'}
            result.append({
                'id': r['id'], 'categoria_id': r['categoria_id'],
                'monto': safe_float(r['monto']),
                'categoria_nombre': cat['nombre'],
                'color': cat['color'], 'icono': cat['icono']
            })
        return result

    def establecer_presupuesto(self, categoria_id: int, mes: int, anio: int, monto: float) -> bool:
        try:
            existing = self.client.table('presupuestos').select('id').eq('categoria_id', int(categoria_id)).eq('mes', int(mes)).eq('anio', int(anio)).execute()
            if existing.data:
                self.client.table('presupuestos').update({'monto': float(monto)}).eq('categoria_id', int(categoria_id)).eq('mes', int(mes)).eq('anio', int(anio)).execute()
            else:
                self.client.table('presupuestos').insert({'categoria_id': int(categoria_id), 'mes': int(mes), 'anio': int(anio), 'monto': float(monto)}).execute()
            return True
        except Exception:
            return False

    # ==================== METAS FINANCIERAS ====================
    def obtener_metas(self, activo: bool = True) -> List[Dict]:
        query = self.client.table('metas_financieras').select('id, nombre, monto_objetivo, monto_actual, fecha_limite, prioridad, descripcion, activo')
        if activo:
            query = query.eq('activo', 1)
        query = query.order('fecha_limite', desc=False)
        response = query.execute()
        result = []
        for r in (response.data or []):
            result.append({
                'id': r['id'], 'nombre': safe_str(r['nombre']),
                'monto_objetivo': safe_float(r['monto_objetivo']),
                'monto_actual': safe_float(r['monto_actual']),
                'fecha_limite': r.get('fecha_limite'),
                'prioridad': safe_str(r['prioridad'], 'media'),
                'descripcion': safe_str(r.get('descripcion')),
                'activo': bool(r.get('activo', 1))
            })
        return result

    def agregar_meta(self, nombre: str, monto_objetivo: float, fecha_limite: Optional[str],
                     prioridad: str = 'media', descripcion: str = '') -> int:
        response = self.client.table('metas_financieras').insert({
            'nombre': nombre, 'monto_objetivo': float(monto_objetivo),
            'fecha_limite': fecha_limite, 'prioridad': prioridad,
            'descripcion': descripcion, 'activo': 1
        }).select('id').execute()
        return response.data[0]['id'] if response.data else 0

    def agregar_aporte_meta(self, meta_id: int, monto: float, fecha: str, notas: str = '') -> int:
        fecha_dt = datetime.fromisoformat(fecha)
        response = self.client.table('aportes_metas').insert({
            'meta_id': int(meta_id), 'monto': float(monto), 'fecha': fecha,
            'mes': fecha_dt.month, 'anio': fecha_dt.year, 'notas': notas
        }).select('id').execute()
        res_sum = self.client.table('aportes_metas').select('monto').eq('meta_id', int(meta_id)).execute()
        total = sum(safe_float(a['monto']) for a in (res_sum.data or []))
        self.client.table('metas_financieras').update({'monto_actual': total}).eq('id', int(meta_id)).execute()
        return response.data[0]['id'] if response.data else 0

    def obtener_aportes_meta_mes(self, meta_id: int, mes: int, anio: int) -> float:
        response = self.client.table('aportes_metas').select('monto').eq('meta_id', int(meta_id)).eq('mes', int(mes)).eq('anio', int(anio)).execute()
        return sum(safe_float(a['monto']) for a in (response.data or []))

    def eliminar_meta(self, id: int) -> bool:
        response = self.client.table('metas_financieras').update({'activo': 0}).eq('id', int(id)).execute()
        return len(response.data) > 0

# ============================================================
# FUNCIONES AUXILIARES - CÁLCULOS FINANCIEROS
# ============================================================
def formatear_moneda(monto: float) -> str:
    return f"S/ {monto:,.2f}"

def calcular_total_ingresos(db: DatabaseManager, mes: int, anio: int) -> float:
    """Calcula el TOTAL de ingresos del mes (recibidos + pendientes)"""
    ingresos = db.obtener_ingresos_mensuales(mes, anio)
    return sum(float(i['monto']) for i in ingresos)

def calcular_total_ingresos_recibidos(db: DatabaseManager, mes: int, anio: int) -> float:
    """Calcula SOLO los ingresos ya recibidos"""
    ingresos = db.obtener_ingresos_mensuales(mes, anio)
    return sum(float(i['monto']) for i in ingresos if i['recibido'])

def calcular_total_gastos_fijos(db: DatabaseManager, mes: int, anio: int) -> float:
    gastos = db.obtener_gastos_fijos_mensuales(mes, anio)
    return sum(float(g['monto']) for g in gastos)

def calcular_total_gastos_fijos_pagados(db: DatabaseManager, mes: int, anio: int) -> float:
    """Calcula SOLO los gastos fijos ya pagados"""
    gastos = db.obtener_gastos_fijos_mensuales(mes, anio)
    return sum(float(g['monto']) for g in gastos if g['pagado'])

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

def calcular_saldo_proyectado(db: DatabaseManager, mes: int, anio: int) -> float:
    """
    SALDO PROYECTADO: Considera TODOS los ingresos del mes (recibidos + pendientes)
    Útil para planificación
    """
    ingresos = calcular_total_ingresos(db, mes, anio)
    egresos = (calcular_total_gastos_fijos(db, mes, anio) +
               calcular_total_gastos_variables(db, mes, anio) +
               calcular_total_prestamos_mes(db, mes, anio) +
               calcular_total_ahorros_mes(db, mes, anio) +
               calcular_total_aportes_metas_mes(db, mes, anio))
    return ingresos - egresos

def calcular_saldo_real_disponible(db: DatabaseManager, mes: int, anio: int) -> float:
    """
    SALDO REAL DISPONIBLE: Considera SOLO los ingresos ya recibidos
    y SOLO los egresos ya ejecutados (gastos fijos pagados + gastos variables + préstamos pagados + ahorros + metas)
    Este es el dinero REAL que tienes en este momento
    """
    ingresos_recibidos = calcular_total_ingresos_recibidos(db, mes, anio)
    # Solo considerar egresos ya ejecutados
    gastos_fijos_pagados = calcular_total_gastos_fijos_pagados(db, mes, anio)
    gastos_variables = calcular_total_gastos_variables(db, mes, anio)
    prestamos_mes = calcular_total_prestamos_mes(db, mes, anio)
    ahorros_mes = calcular_total_ahorros_mes(db, mes, anio)
    metas_mes = calcular_total_aportes_metas_mes(db, mes, anio)
    egresos_ejecutados = gastos_fijos_pagados + gastos_variables + prestamos_mes + ahorros_mes + metas_mes
    return ingresos_recibidos - egresos_ejecutados

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
    """Renderiza las tarjetas de saldo: PROYECTADO y REAL DISPONIBLE"""
    saldo_proyectado = calcular_saldo_proyectado(db, mes, anio)
    saldo_real = calcular_saldo_real_disponible(db, mes, anio)
    ingresos_totales = calcular_total_ingresos(db, mes, anio)
    ingresos_recibidos = calcular_total_ingresos_recibidos(db, mes, anio)

    # Tarjeta de Saldo Real Disponible (la más importante)
    if ingresos_recibidos == 0:
        clase_real, mensaje_real = "", "⚠️ Aún no has registrado ingresos recibidos"
    elif saldo_real < 0:
        clase_real, mensaje_real = "danger", f"🚨 Déficit real: Has gastado más de lo recibido"
    elif saldo_real < ingresos_recibidos * 0.1:
        clase_real, mensaje_real = "warning", f"⚠️ Saldo real bajo: {(saldo_real/ingresos_recibidos)*100:.1f}% de lo recibido"
    else:
        clase_real, mensaje_real = "", "✅ Dinero real disponible en este momento"

    st.markdown(f"""
    <div class="saldo-card {clase_real}">
        <div class="saldo-label">💰 Saldo REAL Disponible - {obtener_nombre_mes(mes, anio)}</div>
        <div class="saldo-amount">{formatear_moneda(saldo_real)}</div>
        <div style="font-size: 0.95rem; opacity: 0.95;">{mensaje_real}</div>
        <div style="font-size: 0.85rem; opacity: 0.9; margin-top: 0.5rem;">
            💵 Ingresos recibidos: {formatear_moneda(ingresos_recibidos)} de {formatear_moneda(ingresos_totales)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tarjeta de Saldo Proyectado (informativa)
    if ingresos_totales > 0:
        porcentaje_recibido = (ingresos_recibidos / ingresos_totales) * 100
        if saldo_proyectado < 0:
            clase_proj = "danger"
        elif saldo_proyectado < ingresos_totales * 0.1:
            clase_proj = "warning"
        else:
            clase_proj = "info"

        st.markdown(f"""
        <div class="saldo-card {clase_proj}" style="opacity: 0.85;">
            <div class="saldo-label">📊 Saldo PROYECTADO (Planificación) - {obtener_nombre_mes(mes, anio)}</div>
            <div class="saldo-amount">{formatear_moneda(saldo_proyectado)}</div>
            <div style="font-size: 0.95rem; opacity: 0.95;">
                Si recibes todos los ingresos pendientes: {formatear_moneda(ingresos_totales - ingresos_recibidos)}
            </div>
            <div style="font-size: 0.85rem; opacity: 0.9; margin-top: 0.5rem;">
                📈 {porcentaje_recibido:.1f}% de ingresos ya recibidos
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_footer():
    st.markdown("""
    <div class="footer-designer">
        <div class="brand">CAVA</div>
        <h4>Especialistas en Robótica y Automatización</h4>
        <p>Diseñado y desarrollado por <strong>Roger Huamani</strong></p>
        <p style="font-size: 0.8rem; opacity: 0.8; margin-top: 0.5rem;">© 2026 - Todos los derechos reservados</p>
    </div>
    """, unsafe_allow_html=True)

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
                    st.rerun()
                else:
                    st.error("El nombre de usuario ya existe")

# ============================================================
# PÁGINA: INICIO (DASHBOARD)
# ============================================================
def pagina_inicio(db: DatabaseManager, mes: int, anio: int):
    st.title(f"🏠 Dashboard - {obtener_nombre_mes(mes, anio)}")
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
    total_egresos = total_gastos_fijos + total_gastos_variables + total_prestamos_mes + total_ahorros + total_aportes_metas

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
        saldo_real = calcular_saldo_real_disponible(db, mes, anio)
        color_saldo = "#198754" if saldo_real >= 0 else "#dc3545"
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid {color_saldo};">
            <div style="font-size: 0.85rem; color: #6c757d; text-transform: uppercase;">💰 Saldo Real</div>
            <div style="font-size: 1.3rem; font-weight: 600; color: {color_saldo};">{formatear_moneda(saldo_real)}</div>
            <div style="font-size: 0.75rem; color: #6c757d;">Disponible ahora</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Distribución del Ingreso")
        if total_ingresos > 0:
            saldo_proyectado = calcular_saldo_proyectado(db, mes, anio)
            data = pd.DataFrame([
                {'Concepto': 'Gastos Fijos', 'Monto': total_gastos_fijos},
                {'Concepto': 'Gastos Variables', 'Monto': total_gastos_variables},
                {'Concepto': 'Préstamos', 'Monto': total_prestamos_mes},
                {'Concepto': 'Ahorros', 'Monto': total_ahorros},
                {'Concepto': 'Metas', 'Monto': total_aportes_metas},
                {'Concepto': 'Disponible', 'Monto': max(saldo_proyectado, 0)}
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
            st.info("💡 Define presupuestos en '📊 Presupuestos'")

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

# Continúa en el siguiente mensaje por límite de caracteres...
