# ☁️ CloudAssign — Asignación Inteligente de Instancias y Servidores Cloud

**Proyecto Integrador Final | Cátedra de Investigación de Operaciones (Unidad 6)**

## 📋 Descripción del Proyecto

**CloudAssign** es una aplicación web interactiva desarrollada en Python que resuelve el problema de asignación óptima de microservicios empresariales hacia instancias de cómputo en la nube (AWS, Azure y Google Cloud Platform) mediante **Programación Lineal Entera Binaria (PLEB)**.

El sistema minimiza el costo operativo por hora garantizando el cumplimiento estricto de:

* Capacidad de memoria RAM (GB) por servidor.
* Capacidad de núcleos de procesamiento (vCPU) por servidor.
* Acuerdos de Nivel de Servicio (SLA) de latencia máxima de red (ms).

## 🧮 Formulación Matemática

* **Variables de decisión:**

  * xij E {0, 1}: 1 si el microservicio i se asigna al servidor j; 0 en caso contrario.
  * yj E {0, 1}: 1 si la instancia cloud j se enciende/contrata; 0 en caso contrario.
* **Función Objetivo:**
Min Z = E{j E J} c\_j . y\_j
* **Restricciones:**

  1. Asignación única: E{j E J} x\_{ij} = 1, ∀ i ∈ I
  2. Capacidad de RAM: E{i E I} r\_i x\_{ij} =< R\_j y\_j, ∀ j ∈ J
  3. Capacidad de vCPU: E{i E I} p\_i x\_{ij} =< P\_j y\_j, ∀ j ∈ J
  4. Latencia SLA: L\_j x\_{ij} =< l\_i, ∀ i ∈ I, j ∈ J

## 🚀 Instalación y Ejecución Local

1. Clona este repositorio o descarga los archivos:

```bash
   git clone https://github.com/Maresx77-GH/cloudassign-io.git
   cd cloudassign-io
   ```

2. Instala las dependencias:

```bash
   pip install -r requirements.txt
   ```

3. Ejecuta la aplicación web interactiva:

```bash
   streamlit run app.py
   ```

4. Abre tu navegador en `http://localhost:8501`.

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3.11+
* **Solver de Optimización:** PuLP + CBC (Coin-or Branch and Cut)
* **Interfaz Web:** Streamlit \& Pandas



\## 📊 Resultados Principales (Escenario Base)



&#x20;Al resolver el modelo de Programación Lineal Entera Binaria (PLEB) con \*\*PuLP\*\* (`pulp==2.9.0`) y el solver \*\*CBC\*\*, se alcanzó una solución \*\*ÓPTIMA (Optimal)\*\*:



\* \*\*Costo mínimo operativo:\*\* \*\*$0.96 USD/h\*\*

\* \*\*Costo mensual proyectado (720 h):\*\* \*\*$691.20 USD\*\*

\* \*\*Ahorro operativo:\*\* \*\*36.4%\*\* (\*\*$396.00 USD/mes\*\* ahorrados frente al escenario base)

\* \*\*Servidores activos (`y\_j = 1`):\*\*

&#x20; \* \*\*S1 (`AWS c6i.2xlarge`, US-East):\*\* `$0.34/h` — aloja \*\*M1\*\*, \*\*M2\*\* y \*\*M4\*\*; uso de `16/16 GB` RAM (`100.0%`, `0 GB` de holgura) y `8/8 vCPU` (`100.0%`, `0 vCPU` de holgura)

&#x20; \* \*\*S3 (`GCP n2-standard-16`, US-Central):\*\* `$0.62/h` — aloja \*\*M3\*\* y \*\*M5\*\*; uso de `28/64 GB` RAM (`43.8%`, `36 GB` de holgura) y `12/16 vCPU` (`75.0%`, `4 vCPU` de holgura)

\* \*\*Servidores apagados (`y\_j = 0`):\*\* \*\*S2\*\* (`Azure Standard\_D8s\_v5`) y \*\*S4\*\* (`AWS t3.xlarge`) permanecen inactivas (`$0.00/h`), cumpliéndose el \*\*100%\*\* de las restricciones de capacidad y latencia (SLA).

