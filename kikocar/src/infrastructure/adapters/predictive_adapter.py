from decimal import Decimal
from math import exp
from typing import Optional, Tuple


class PredictiveAdapter:
    """
    Modelo de diagnóstico multi-variable (árbol de decisión mejorado).
    Evalúa:

      Variables de entrada:
        - horas_desde_ultimo_mant : horas acumuladas desde último mant.
        - intervalo_mant_horas    : intervalo programado entre mant.
        - horas_totales_maquina   : vida total de la máquina (horómetro)
        - capacidad_ton           : capacidad en toneladas
        - tipo_equipo             : "oruga", "movil", "todoterreno"
        - consumo_teorico_gh      : galones/hora teóricos
        - relacion_consumo_real   : consumo_real / consumo_teorico (>1.15 = alerta)
        - alertas_previas         : número de alertas de robo previas
    """

    PESO_MANTENIMIENTO = 0.45
    PESO_VIDA = 0.20
    PESO_CONSUMO = 0.15
    PESO_CAPACIDAD = 0.10
    PESO_ALERTAS = 0.10

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
        # 1. Score por mantenimiento (base)
        horas_rel = horas_desde_ultimo_mant / max(intervalo_mant_horas, 1)
        score_mant = min(horas_rel, 2.0)

        # 2. Score por vida útil (fatiga acumulada)
        vida_util_estimada = 15000
        score_vida = min(horas_totales_maquina / vida_util_estimada, 1.5)

        # 3. Score por consumo anómalo (desgaste)
        score_consumo = max(0, (relacion_consumo_real - 1.0) * 2)

        # 4. Score por capacidad (más tonelaje = más estrés)
        score_capacidad = min(capacidad_ton / 500, 1.0)

        # 5. Score por historial de alertas
        score_alertas = min(alertas_previas * 0.15, 1.0)

        # 6. Factor por tipo de frente
        frente_factor = {"pesado": 1.3, "moderado": 1.0, "ligero": 0.7}.get(
            tipo_frente.lower(), 1.0
        )

        # 7. Factor por tipo de equipo
        equipo_factor = {"oruga": 1.2, "todoterreno": 1.1, "movil": 1.0}.get(
            tipo_equipo.lower(), 1.0
        )

        score_total = (
            score_mant * self.PESO_MANTENIMIENTO
            + score_vida * self.PESO_VIDA
            + score_consumo * self.PESO_CONSUMO
            + score_capacidad * self.PESO_CAPACIDAD
            + score_alertas * self.PESO_ALERTAS
        ) * frente_factor * equipo_factor

        probabilidad = min(round(score_total * 100, 2), 99.99)

        # Días restantes para mantenimiento
        horas_restantes = max(intervalo_mant_horas - horas_desde_ultimo_mant, 0)
        dias_trabajo = 8
        dias_restantes = int(horas_restantes / dias_trabajo)

        # Penalizar días si score es muy alto
        if score_total > 1.5:
            dias_restantes = max(dias_restantes - int(score_total * 10), 0)

        return (probabilidad, dias_restantes)

    def obtener_criticidad(self, probabilidad: float) -> str:
        if probabilidad >= 85:
            return "CRÍTICO"
        elif probabilidad >= 60:
            return "MEDIO"
        return "BAJO"

    def diagnosticar(self, probabilidad: float, dias_restantes: int) -> str:
        if probabilidad >= 85:
            return "REQUIERE MANTENIMIENTO INMEDIATO"
        elif probabilidad >= 60:
            return f"Programar mantenimiento en {dias_restantes} dias"
        elif probabilidad >= 30:
            return f"Monitoreo normal - prox. mant. en {dias_restantes} dias"
        return "Equipo en condiciones optimas"
