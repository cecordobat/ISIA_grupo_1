# Diagramas del Sistema
**Motor de Cumplimiento — Colombia**

*Todos los diagramas están en formato Mermaid. Renderizables en GitHub, VS Code y Google Antigravity.*

---

## Diagrama 1 — Flujo Principal de Liquidación Mensual

```mermaid
flowchart TD
    A([Inicio]) --> B[RF-01: Perfil del contratista\nCC, EPS, AFP, CIIU]
    B --> C[RF-02: Registro de contratos\nValor, fechas, nivel ARL]
    C --> D{¿Contratos parciales\nen el período?}
    D -->|Sí| E[RN-05: Proporcionalidad\npor días]
    D -->|No| F
    E --> F[RF-03: Consolidación\nIngreso Bruto Total]
    F --> G[RF-04: Costos Presuntos CIIU\n+ Regla del 40%]
    G --> H{CT-01: ¿IBC en rango\n1 a 25 SMMLV?}
    H -->|No| ERR1[❌ Error Bloqueante\nAjuste manual]
    H -->|Sí| I{¿Ingreso Neto\n< 1 SMMLV?}
    I -->|Sí| J[RF-05: Piso Protección Social\nBEPS vs SMMLV completo]
    J --> K{¿Usuario eligió\nopción?}
    K -->|No| WAIT[⏳ Esperar decisión]
    K -->|Sí| L
    I -->|No| L[RF-06: Aportes SGSSI\nSalud + Pensión + ARL]
    L --> M{CT-02: ¿Suma aportes\n≈ IBC × tasas?}
    M -->|No| ERR2[❌ Error de Cálculo]
    M -->|Sí| N[RF-07: Depuración Base Gravable\nRetención Art. 383 E.T.]
    N --> O{CT-03: ¿Base = Ingresos\n- Salud - Pensión?}
    O -->|No| ERR3[❌ Error de Consistencia]
    O -->|Sí| P[RF-08: Resumen Pre-Liquidación\nPDF exportable]
    P --> Q[RF-09: Historial\nSnapshot Normativo]
    Q --> Z([Fin])
```

---

## Diagrama 2 — Actores y sus Interacciones

```mermaid
graph LR
    subgraph Actores Primarios
        CI[👤 Contratista\nIndependiente]
        CO[👔 Contador /\nAsesor Tributario]
    end

    subgraph Motor de Cumplimiento
        MO[🔄 Motor de Cálculo\nfunción pura]
        BD[(🗄️ Base de Datos)]
        PDF[📄 Generador PDF]
    end

    subgraph Externos Solo Referencia
        PILA[💻 Operador PILA\nSOI / Mi Planilla]
        UGPP[⚖️ UGPP\nFiscalización]
        DIAN[📋 DIAN\nTablas normativas]
    end

    CI -->|Registra contratos\ne ingresos| MO
    CO -->|Revisa y valida\nliquidaciones| MO
    MO -->|Lee parámetros| BD
    MO -->|Guarda liquidación\ninmutable| BD
    MO -->|Genera| PDF
    CI -->|Transcribe valores\nmanualmente| PILA
    CI -.->|Puede ser\nauditado por| UGPP
    DIAN -.->|Publica tablas\nCIIU y retención| BD
```

---

## Diagrama 3 — Modelo de Dominio (Entidades Principales)

```mermaid
erDiagram
    PerfilContratista {
        uuid id PK
        string numero_documento UK
        string tipo_documento
        string nombre_completo
        string ciiu_codigo FK
        enum estado
        timestamp created_at
    }
    Contrato {
        uuid id PK
        uuid contratista_id FK
        string entidad_contratante
        decimal valor_bruto_mensual
        enum nivel_arl
        date fecha_inicio
        date fecha_fin
        enum estado
    }
    LiquidacionPeriodo {
        uuid id PK
        uuid contratista_id FK
        char periodo
        decimal ingreso_bruto_total
        decimal costos_presuntos
        decimal ibc
        decimal aporte_salud
        decimal aporte_pension
        decimal aporte_arl
        decimal retencion_fuente
        uuid snapshot_normativo_id FK
        timestamp generado_en
    }
    SnapshotNormativo {
        uuid id PK
        decimal smmlv
        decimal uvt
        decimal pct_salud
        decimal pct_pension
        json tabla_arl
        int vigencia_anio
    }
    TablaParametroCIIU {
        string codigo_ciiu PK
        string descripcion
        decimal pct_costos_presuntos
        date vigente_desde
    }

    PerfilContratista ||--o{ Contrato : "tiene"
    PerfilContratista ||--o{ LiquidacionPeriodo : "genera"
    LiquidacionPeriodo }o--|| SnapshotNormativo : "usa"
    PerfilContratista }o--|| TablaParametroCIIU : "clasifica con"
```

---

## Diagrama 4 — Arquitectura de Módulos (src/)

```mermaid
graph TD
    subgraph API Layer
        API[FastAPI / REST]
    end

    subgraph Application Layer src/application
        UC_LIQ[CasoUso: EjecutarLiquidacion]
        UC_REG[CasoUso: RegistrarContrato]
        UC_HIST[CasoUso: ConsultarHistorial]
    end

    subgraph Domain src/domain
        ENT[Entidades: PerfilContratista\nContrato, LiquidacionPeriodo]
        RULES[Reglas de Negocio RN-01..RN-08]
    end

    subgraph Módulos de Cálculo src/mod-calculo
        IBC[Calculador IBC\nRN-01 a RN-05]
        APORTES[Calculador Aportes\nRN-03, RN-08]
        RETEN[Calculador Retención\nRN-07, Art. 383]
    end

    subgraph Módulos de Soporte
        PARAMS[mod-parametros\nSMMLV, CIIU, ARL]
        HIST[mod-historial\nSnapshot + APPEND-ONLY]
        LIQ[mod-liquidacion\nOrquesta el flujo]
    end

    subgraph Infrastructure src/infrastructure
        REPO[Repositorios BD]
        PDF_GEN[Generador PDF]
    end

    API --> UC_LIQ
    API --> UC_REG
    API --> UC_HIST
    UC_LIQ --> LIQ
    LIQ --> IBC
    LIQ --> APORTES
    LIQ --> RETEN
    IBC --> PARAMS
    APORTES --> PARAMS
    LIQ --> HIST
    UC_REG --> REPO
    UC_HIST --> REPO
    HIST --> REPO
    LIQ --> PDF_GEN
```

---

## Diagrama 5 — Dependencia Circular Resuelta (Aportes → Retención)

```mermaid
sequenceDiagram
    participant U as Usuario
    participant M as Motor de Cálculo
    participant P as Parámetros Normativos

    U->>M: Ingresos + Contratos + Período
    M->>P: Obtener SMMLV, %Salud, %Pensión, tabla CIIU
    M->>M: 1. Calcular IBC (regla del 40%)
    M->>M: 2. Calcular Salud = IBC × 12.5%
    M->>M: 3. Calcular Pensión = IBC × 16%
    Note over M: Los aportes se calculan PRIMERO
    M->>P: Obtener tabla Art. 383 E.T.
    M->>M: 4. Base Gravable = Ingreso − Salud − Pensión
    M->>M: 5. Retención = f(Base_Gravable, tabla_383)
    Note over M: La retención usa los aportes ya calculados
    M-->>U: IBC + Aportes + Retención + Neto
```