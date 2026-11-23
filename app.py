import streamlit as st
import pandas as pd
import pulp

# Configuración de página
st.set_page_config(
    page_title="CloudAssign | Optimización de Infraestructura Cloud",
    page_icon="☁️",
    layout="wide"
)

st.title("☁️ CloudAssign — Asignación Inteligente de Instancias y Servidores Cloud")
st.markdown(
    "**Proyecto Integrador Final • Investigación de Operaciones (Unidad 6)** | "
    "Motor de Programación Lineal Entera Binaria (`PuLP` + Solver `CBC`)"
)
st.divider()

# Datos por defecto (alineados al documento técnico)
default_microservices = pd.DataFrame([
    {"ID": "M1", "Microservicio": "Servicio de Autenticación (OAuth2)", "RAM_GB": 4, "vCPU": 2, "Latencia_Max_ms": 25},
    {"ID": "M2", "Microservicio": "Pasarela de Pagos y Facturación", "RAM_GB": 8, "vCPU": 4, "Latencia_Max_ms": 15},
    {"ID": "M3", "Microservicio": "Catálogo y Motor de Búsqueda", "RAM_GB": 12, "vCPU": 4, "Latencia_Max_ms": 30},
    {"ID": "M4", "Microservicio": "Cola de Notificaciones y Correos", "RAM_GB": 4, "vCPU": 2, "Latencia_Max_ms": 45},
    {"ID": "M5", "Microservicio": "Motor de Analítica en Tiempo Real", "RAM_GB": 16, "vCPU": 8, "Latencia_Max_ms": 35},
])

default_servers = pd.DataFrame([
    {"ID": "S1", "Instancia_Cloud": "AWS c6i.2xlarge (US-East)", "Cap_RAM_GB": 16, "Cap_vCPU": 8, "Latencia_ms": 12, "Costo_Hora_USD": 0.34},
    {"ID": "S2", "Instancia_Cloud": "Azure Standard_D8s_v5 (Central)", "Cap_RAM_GB": 32, "Cap_vCPU": 8, "Latencia_ms": 18, "Costo_Hora_USD": 0.38},
    {"ID": "S3", "Instancia_Cloud": "GCP n2-standard-16 (US-Central)", "Cap_RAM_GB": 64, "Cap_vCPU": 16, "Latencia_ms": 22, "Costo_Hora_USD": 0.62},
    {"ID": "S4", "Instancia_Cloud": "AWS t3.xlarge (US-West)", "Cap_RAM_GB": 16, "Cap_vCPU": 4, "Latencia_ms": 40, "Costo_Hora_USD": 0.17},
])

# Sección interactiva de entrada de datos
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("1. Demanda de Microservicios (Parámetros i)")
    st.caption("Puedes editar valores directamente en la tabla para simular escenarios:")
    df_ms = st.data_editor(default_microservices, use_container_width=True, num_rows="dynamic", key="ms_editor")

with col_right:
    st.subheader("2. Catálogo de Servidores Cloud (Parámetros j)")
    st.caption("Modifica capacidades, latencias o tarifas por hora ($ USD):")
    df_srv = st.data_editor(default_servers, use_container_width=True, num_rows="dynamic", key="srv_editor")

def resolver_modelo(microservices_df: pd.DataFrame, servers_df: pd.DataFrame):
    ms_list = microservices_df.to_dict("records")
    srv_list = servers_df.to_dict("records")

    I = [m["ID"] for m in ms_list]
    J = [s["ID"] for s in srv_list]

    r = {m["ID"]: float(m["RAM_GB"]) for m in ms_list}
    p = {m["ID"]: float(m["vCPU"]) for m in ms_list}
    l_max = {m["ID"]: float(m["Latencia_Max_ms"]) for m in ms_list}
    ms_name = {m["ID"]: m["Microservicio"] for m in ms_list}

    R = {s["ID"]: float(s["Cap_RAM_GB"]) for s in srv_list}
    P = {s["ID"]: float(s["Cap_vCPU"]) for s in srv_list}
    L = {s["ID"]: float(s["Latencia_ms"]) for s in srv_list}
    c = {s["ID"]: float(s["Costo_Hora_USD"]) for s in srv_list}
    srv_name = {s["ID"]: s["Instancia_Cloud"] for s in srv_list}

    # Modelo PLEB en PuLP
    prob = pulp.LpProblem("CloudAssign_PLEB", pulp.LpMinimize)

    # Variables de decisión binarias
    x = {
        (i, j): pulp.LpVariable(f"x_{i}_{j}", cat=pulp.LpBinary)
        for i in I
        for j in J
    }
    y = {
        j: pulp.LpVariable(f"y_{j}", cat=pulp.LpBinary)
        for j in J
    }

    # Función Objetivo: Minimizar costo operativo total por hora
    prob += pulp.lpSum(c[j] * y[j] for j in J), "Costo_Total_Hora"

    # Restricción 1: Cada microservicio debe asignarse exactamente a 1 servidor
    for i in I:
        prob += pulp.lpSum(x[(i, j)] for j in J) == 1, f"Asignacion_Unica_{i}"

    # Restricción 2: Capacidad máxima de Memoria RAM por servidor
    for j in J:
        prob += pulp.lpSum(r[i] * x[(i, j)] for i in I) <= R[j] * y[j], f"Capacidad_RAM_{j}"

    # Restricción 3: Capacidad máxima de vCPU por servidor
    for j in J:
        prob += pulp.lpSum(p[i] * x[(i, j)] for i in I) <= P[j] * y[j], f"Capacidad_vCPU_{j}"

    # Restricción 4: Cumplimiento estricto de latencia máxima (SLA)
    for i in I:
        for j in J:
            if L[j] > l_max[i]:
                prob += x[(i, j)] == 0, f"SLA_Latencia_{i}_{j}"

    # Resolver con CBC
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    status = pulp.LpStatus[prob.status]

    if status != "Optimal":
        return status, None, None, None

    costo_optimo = pulp.value(prob.objective)
    costo_base_todos = sum(c[j] for j in J)

    # Construir tabla de asignaciones
    asignaciones = []
    for i in I:
        for j in J:
            if pulp.value(x[(i, j)]) > 0.5:
                margen_lat = l_max[i] - L[j]
                asignaciones.append({
                    "ID": i,
                    "Microservicio Asignado": ms_name[i],
                    "Servidor Destino": f"{j}: {srv_name[j]}",
                    "RAM (GB)": int(r[i]),
                    "vCPU": int(p[i]),
                    "Latencia Req / Nodo": f"{int(l_max[i])} ms / {int(L[j])} ms",
                    "Margen SLA": f"Cumple (-{int(margen_lat)} ms)"
                })

    # Construir tabla de utilización y holguras (Slack)
    servidores_res = []
    for j in J:
        activo = pulp.value(y[j]) > 0.5
        ram_usada = sum(r[i] * pulp.value(x[(i, j)]) for i in I)
        cpu_usado = sum(p[i] * pulp.value(x[(i, j)]) for i in I)
        servidores_res.append({
            "Instancia": f"{j}: {srv_name[j]}",
            "Estado": "ACTIVA (y=1)" if activo else "APAGADA (y=0)",
            "Costo ($/h)": f"${c[j]:.2f}" if activo else "$0.00",
            "RAM Usada / Cap.": f"{int(ram_usada)} / {int(R[j])} GB ({(ram_usada/R[j])*100:.1f}%)",
            "Holgura RAM": f"{int(R[j] - ram_usada)} GB",
            "vCPU Usado / Cap.": f"{int(cpu_usado)} / {int(P[j])} vCPU ({(cpu_usado/P[j])*100:.1f}%)",
            "Holgura vCPU": f"{int(P[j] - cpu_usado)} vCPU"
        })

    return status, costo_optimo, costo_base_todos, (pd.DataFrame(asignaciones), pd.DataFrame(servidores_res))

st.divider()
status, z_opt, z_base, tablas = resolver_modelo(df_ms, df_srv)

if status == "Optimal":
    df_asig, df_uso = tablas
    ahorro_hora = z_base - z_opt
    ahorro_pct = (ahorro_hora / z_base * 100) if z_base > 0 else 0

    st.subheader("3. Resultados de la Optimización Global")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Estado del Solver", "ÓPTIMO (Optimal)")
    m2.metric("Costo Mínimo (Z*)", f"${z_opt:.2f} USD/h", f"-${ahorro_hora:.2f}/h vs Base")
    m3.metric("Costo Mensual (720h)", f"${z_opt * 720:,.2f} USD")
    m4.metric("Ahorro Operativo", f"{ahorro_pct:.1f}%", f"${ahorro_hora * 720:,.2f}/mes ahorrados")

    st.markdown("#### Matriz Óptima de Despliegue de Microservicios")
    st.dataframe(df_asig, use_container_width=True, hide_index=True)

    st.markdown("#### Análisis de Utilización de Capacidad y Holguras (Slack)")
    st.dataframe(df_uso, use_container_width=True, hide_index=True)

    st.info(
        "💡 **Interpretación Gerencial:** El motor PLEB consolidó las cargas críticas cumpliendo el 100% de los SLA de latencia "
        "y apagando instancias redundantes para minimizar el gasto operativo."
    )
else:
    st.error(f"⚠️ El modelo resultó **{status}**. Verifica que exista al menos un servidor que cumpla las restricciones de RAM, vCPU y latencia de cada microservicio.")
