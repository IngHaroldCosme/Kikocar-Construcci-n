import io
import json
import os
import pickle
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_graphviz, plot_tree

MODEL_PATH = Path(__file__).parent / "modelo_arbol.pkl"
METRICS_PATH = Path(__file__).parent / "metricas_ml.json"
PLOT_PATH = Path(__file__).parent / "arbol_decision.png"
CM_PATH = Path(__file__).parent / "matriz_confusion.png"


def generar_datos_sinteticos(n=5000, seed=42):
    rng = np.random.default_rng(seed)

    # Features (todas normalizadas a ~0-1 o valores reales)
    horas_desde_mant = rng.uniform(0, 500, n)
    intervalo_mant = rng.uniform(100, 500, n)
    horas_totales = rng.uniform(100, 20000, n)
    capacidad_ton = rng.choice([50, 80, 100, 150, 200, 300, 450, 500], n)
    tipo = rng.choice(["oruga", "movil", "todoterreno"], n)
    consumo_real = rng.uniform(0.5, 3.0, n)
    alertas = rng.integers(0, 6, n)

    tipo_factor = np.array([1.2 if t == "oruga" else 1.1 if t == "todoterreno" else 1.0 for t in tipo])
    vida_util = 15000

    score_mant = np.clip(horas_desde_mant / np.maximum(intervalo_mant, 1), 0, 2)
    score_vida = np.clip(horas_totales / vida_util, 0, 1.5)
    score_consumo = np.clip((consumo_real - 1.0) * 2, 0, 3)
    score_capacidad = np.clip(capacidad_ton / 500, 0, 1)
    score_alertas = np.clip(alertas * 0.15, 0, 1)

    score_total = (
        score_mant * 0.45
        + score_vida * 0.20
        + score_consumo * 0.15
        + score_capacidad * 0.10
        + score_alertas * 0.10
    ) * tipo_factor

    prob = np.clip(score_total * 100 + rng.normal(0, 8, n), 0, 99)

    # Target: 0=BAJO, 1=MEDIO, 2=CRITICO
    y = np.where(prob < 40, 0, np.where(prob < 70, 1, 2))

    X = np.column_stack([
        score_mant,
        score_vida,
        score_consumo,
        score_capacidad,
        score_alertas,
        tipo_factor,
    ])

    return X, y, prob


def entrenar_y_evaluar():
    print("Generando datos sinteticos...")
    X, y, prob = generar_datos_sinteticos(8000)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    print("Entrenando Decision Tree...")
    clf = DecisionTreeClassifier(
        max_depth=5,
        min_samples_split=20,
        min_samples_leaf=10,
        random_state=42,
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(
        y_test, y_pred,
        target_names=["BAJO", "MEDIO", "CRITICO"],
        output_dict=True,
        zero_division=0,
    )

    print(f"\nAccuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print(f"\nMatriz de confusion:\n{cm}")

    # ── Guardar modelo ──
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)
    print(f"\nModelo guardado en {MODEL_PATH}")

    # ── Guardar metricas como JSON ──
    metrics = {
        "accuracy": round(acc, 4),
        "precision_weighted": round(prec, 4),
        "recall_weighted": round(rec, 4),
        "f1_weighted": round(f1, 4),
        "confusion_matrix": cm.tolist(),
        "classification_report": report,
        "clases": ["BAJO", "MEDIO", "CRITICO"],
        "feature_names": [
            "score_mant",
            "score_vida",
            "score_consumo",
            "score_capacidad",
            "score_alertas",
            "tipo_factor",
        ],
        "feature_importances": clf.feature_importances_.tolist(),
        "n_entrenamiento": int(len(X_train)),
        "n_prueba": int(len(X_test)),
        "profundidad": int(clf.get_depth()),
        "n_hojas": int(clf.get_n_leaves()),
    }
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print(f"Metricas guardadas en {METRICS_PATH}")

    # ── Grafico: Arbol de decision (primeros niveles) ──
    plt.figure(figsize=(24, 14))
    plot_tree(
        clf,
        max_depth=3,
        feature_names=metrics["feature_names"],
        class_names=["BAJO", "MEDIO", "CRITICO"],
        filled=True,
        rounded=True,
        fontsize=10,
        proportion=True,
    )
    plt.title("Arbol de Decision - Mantenimiento Predictivo (3 primeros niveles)", fontsize=14, fontweight="bold")
    plt.savefig(PLOT_PATH, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Grafico del arbol guardado en {PLOT_PATH}")

    # ── Grafico: Matriz de confusion ──
    fig, ax = plt.subplots(figsize=(7, 6))
    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["BAJO", "MEDIO", "CRITICO"],
    )
    disp.plot(ax=ax, cmap="Blues", values_format="d")
    ax.set_title("Matriz de Confusion - Decision Tree", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(CM_PATH, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Matriz de confusion guardada en {CM_PATH}")

    # ── Grafico: Importancia de características ──
    plt.figure(figsize=(10, 5))
    names = metrics["feature_names"]
    importances = clf.feature_importances_
    indices = np.argsort(importances)[::-1]
    plt.bar(range(len(importances)), importances[indices], color="#2B3E50")
    plt.xticks(range(len(importances)), [names[i] for i in indices], rotation=30, ha="right")
    plt.title("Importancia de Variables Predictivas", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / "importancia_vars.png", dpi=200, bbox_inches="tight")
    plt.close()
    print("Grafico de importancia guardado")

    # ── Reporte de texto para PPT ──
    print("\n" + "=" * 60)
    print("RESUMEN PARA PPT")
    print("=" * 60)
    print(f"Modelo: DecisionTreeClassifier (max_depth=5)")
    print(f"Datos de entrenamiento: {metrics['n_entrenamiento']} muestras")
    print(f"Datos de prueba: {metrics['n_prueba']} muestras")
    print(f"Profundidad del arbol: {metrics['profundidad']}")
    print(f"Numero de hojas: {metrics['n_hojas']}")
    print(f"")
    print(f"Accuracy:  {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision_weighted']:.4f}")
    print(f"Recall:    {metrics['recall_weighted']:.4f}")
    print(f"F1-Score:  {metrics['f1_weighted']:.4f}")
    print(f"")
    print("Matriz de confusion:")
    print(f"{'':>10} {'BAJO':>8} {'MEDIO':>8} {'CRITICO':>8}")
    for i, label in enumerate(["BAJO", "MEDIO", "CRITICO"]):
        print(f"{label:>10} {cm[i][0]:>8} {cm[i][1]:>8} {cm[i][2]:>8}")
    print(f"")
    print("Falsos Positivos (FP) por clase:")
    for i, label in enumerate(["BAJO", "MEDIO", "CRITICO"]):
        fp = cm[:, i].sum() - cm[i, i]
        fn = cm[i, :].sum() - cm[i, i]
        print(f"  {label}: FP={fp}, FN={fn}")
    print(f"")
    print("Importancia de variables:")
    for i in indices:
        print(f"  {names[i]:25s}: {importances[i]:.3f}")

    return clf, metrics


if __name__ == "__main__":
    entrenar_y_evaluar()
