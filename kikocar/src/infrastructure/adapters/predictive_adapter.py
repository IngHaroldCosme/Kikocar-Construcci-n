import os
import pickle
from pathlib import Path
from typing import Tuple

import numpy as np

_MODEL_PATH = Path(__file__).parent.parent.parent / "backend" / "modelo_arbol.pkl"


def _cargar_modelo():
    if _MODEL_PATH.exists():
        with open(_MODEL_PATH, "rb") as f:
            return pickle.load(f)
    return None


_MODELO = None
_LOADED = False


def _get_model():
    global _MODELO, _LOADED
    if not _LOADED:
        _MODELO = _cargar_modelo()
        _LOADED = True
    return _MODELO


class PredictiveAdapter:
    """
    Modelo de Machine Learning: Decision Tree (scikit-learn).
    Entrenado con 8000 muestras sinteticas basadas en reglas de ingenieria.

    Features de entrada (6):
      - score_mant      : horas_desde_ultimo_mant / intervalo_mant_horas (0-2)
      - score_vida      : horas_totales_maquina / 15000 (0-1.5)
      - score_consumo   : (relacion_consumo_real - 1.0) * 2 (0-3)
      - score_capacidad : capacidad_ton / 500 (0-1)
      - score_alertas   : alertas_previas * 0.15 (0-1)
      - tipo_factor     : 1.2 oruga, 1.1 todoterreno, 1.0 movil
    """

    def evaluar(
        self,
        horas_desde_ultimo_mant: float,
        intervalo_mant_horas: float,
        horas_totales_maquina: float = 0,
        capacidad_ton: int = 0,
        tipo_equipo: str = "movil",
        consumo_teorico_gh: float = 10,
        relacion_consumo_real: float = 1.0,
        alertas_previas: int = 0,
        tipo_frente: str = "moderado",
    ) -> Tuple[float, int]:
        # Calcular features
        score_mant = min(horas_desde_ultimo_mant / max(intervalo_mant_horas, 1), 2.0)
        score_vida = min(horas_totales_maquina / 15000, 1.5)
        score_consumo = max(0, (relacion_consumo_real - 1.0) * 2)
        score_capacidad = min(capacidad_ton / 500, 1.0)
        score_alertas = min(alertas_previas * 0.15, 1.0)

        tipo_factor = {"oruga": 1.2, "todoterreno": 1.1, "movil": 1.0}.get(
            tipo_equipo.lower(), 1.0
        )

        features = np.array([[
            score_mant,
            score_vida,
            score_consumo,
            score_capacidad,
            score_alertas,
            tipo_factor,
        ]])

        modelo = _get_model()
        if modelo is not None:
            clase = int(modelo.predict(features)[0])
            proba = modelo.predict_proba(features)[0]

            # Probabilidad como el maximo de las probabilidades predichas
            probabilidad = round(float(proba[clase] * 100), 2)

            # Horas restantes para mantenimiento
            horas_rest = max(intervalo_mant_horas - horas_desde_ultimo_mant, 0)
            horas_rest_int = int(round(horas_rest))

            # Penalizar horas si es CRITICO o MEDIO
            if clase == 2:
                horas_rest_int = max(horas_rest_int - 40, 0)
            elif clase == 1:
                horas_rest_int = max(horas_rest_int - 16, 0)

            return (probabilidad, horas_rest_int)

        # Fallback heuristico si no hay modelo
        score_total = (
            score_mant * 0.45
            + score_vida * 0.20
            + score_consumo * 0.15
            + score_capacidad * 0.10
            + score_alertas * 0.10
        ) * tipo_factor

        probabilidad = min(round(score_total * 100, 2), 99.99)
        horas_rest = max(intervalo_mant_horas - horas_desde_ultimo_mant, 0)
        horas_rest_int = int(round(horas_rest))
        if score_total > 1.5:
            horas_rest_int = max(horas_rest_int - int(score_total * 80), 0)

        return (probabilidad, horas_rest_int)

    def obtener_criticidad(self, probabilidad: float) -> str:
        modelo = _get_model()
        if modelo is not None:
            # Mapear probabilidad a clase
            if probabilidad >= 70:
                return "CRITICO"
            elif probabilidad >= 35:
                return "MEDIO"
            return "BAJO"
        if probabilidad >= 85:
            return "CRITICO"
        elif probabilidad >= 60:
            return "MEDIO"
        return "BAJO"

    def diagnosticar(self, probabilidad: float, horas_restantes: int) -> str:
        modelo = _get_model()
        if modelo is not None:
            if probabilidad >= 70:
                return "REQUIERE MANTENIMIENTO INMEDIATO"
            elif probabilidad >= 35:
                return f"Programar mantenimiento en {horas_restantes} h"
            return "Equipo en condiciones optimas"
        if probabilidad >= 85:
            return "REQUIERE MANTENIMIENTO INMEDIATO"
        elif probabilidad >= 60:
            return f"Programar mantenimiento en {horas_restantes} h"
        elif probabilidad >= 30:
            return f"Monitoreo normal - prox. mant. en {horas_restantes} h"
        return "Equipo en condiciones optimas"
