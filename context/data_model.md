# Modelo de Datos

## Entidades principales

### PerfilContratista
- id
- tipo_documento
- numero_documento
- nombre_completo
- eps
- afp
- ciiu_codigo
- estado
- created_at

### Contrato
- id
- perfil_id
- entidad_contratante
- valor_bruto_mensual
- nivel_arl
- fecha_inicio
- fecha_fin
- estado

### LiquidacionPeriodo
- id
- perfil_id
- periodo
- ingreso_bruto_total
- costos_presuntos
- ibc
- aporte_salud
- aporte_pension
- aporte_arl
- nivel_arl_aplicado
- retencion_fuente
- base_gravable_retencion
- opcion_piso_proteccion
- snapshot_normativo_id
- generado_en

### SnapshotNormativo
- id
- smmlv
- uvt
- pct_salud
- pct_pension
- tabla_arl_json
- vigencia_anio
- created_at

### TablaParametroCIIU
- codigo_ciiu
- descripcion
- pct_costos_presuntos
- vigente_desde

### TablaRetencion383
- id
- uvt_desde
- uvt_hasta
- tarifa_marginal
- uvt_deduccion
- vigente_desde

### AccesoContadorPerfil
- id
- contador_id
- perfil_id
- creado_en

### LiquidacionRevision
- id
- liquidacion_id
- contador_id
- nota
- aprobada
- revisado_en

### LiquidacionConfirmacion
- id
- liquidacion_id
- usuario_id
- confirmado_en

## Relaciones clave
- Un perfil tiene muchos contratos.
- Un perfil tiene muchas liquidaciones.
- Cada liquidacion usa un snapshot normativo.
- Un contador puede tener acceso a muchos perfiles autorizados.
- Una liquidacion puede tener una revision y una confirmacion asociadas.
