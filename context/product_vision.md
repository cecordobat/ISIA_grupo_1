# Vision del Producto

**Motor de Cumplimiento Tributario y Seguridad Social para Contratistas Independientes - Colombia**

## Problema que resuelve
El producto busca asistir a contratistas independientes que deben autoliquidar aportes y retenciones sin apoyo contable especializado, reduciendo errores y riesgo sancionatorio.

## Propuesta de valor
El sistema:

1. Guia al contratista paso a paso desde ingresos hasta resumen final.
2. Consolida multiples contratos en un unico IBC mensual.
3. Aplica costos presuntos segun CIIU.
4. Explica el Piso de Proteccion Social cuando aplica.
5. Calcula aportes antes de retencion para respetar la dependencia normativa.
6. Genera una pre-liquidacion en PDF.
7. Guarda historico auditable con snapshot normativo.

## Actores objetivo
| Actor | Necesidad principal |
|---|---|
| Contratista independiente | Calcular correctamente sin conocimientos tecnicos |
| Contador o asesor tributario | Revisar multiples clientes y validar liquidaciones |
| Entidad contratante | Verificar cumplimiento antes de pagar honorarios |

## Alcance actual
- Registro de perfil del contratista.
- Registro y consolidacion de contratos.
- Calculo de IBC, aportes y retencion.
- Historial de liquidaciones con snapshot normativo.
- Flujo de revision por contador y confirmacion del contratista.
- Generacion de PDF resumen.

## Capacidades pendientes priorizadas
Las siguientes capacidades forman parte del alcance objetivo definido en la segunda entrega del proyecto, pero aun no se consideran totalmente implementadas en el estado actual del sistema:

1. Administracion funcional de parametros normativos por rol administrador.
2. Portal o vista de verificacion para entidad contratante.
3. Rol administrador visible como actor operativo del producto.
4. MFA para contador o asesor tributario.
5. Comparacion entre liquidaciones de distintos periodos.
6. Evidencia de cumplimiento mas clara para terceros autorizados.

## Fuera de alcance
- No genera archivo plano Tipo 2 PILA.
- No integra APIs de UGPP, DIAN ni operadores PILA.
- No reemplaza asesoria contable certificada.
- No valida ingresos contra facturacion electronica real.
- No realiza el pago, solo entrega el resumen para transcripcion.

## Vision futura
La arquitectura debe permitir incorporar cambios regulatorios futuros, especialmente los derivados de la Ley 2381 de 2024 y ajustes anuales de SMMLV, UVT, ARL, CIIU o tabla de retencion.

La vision futura tambien incluye:

- administracion segura de tablas y snapshots normativos sin hardcode operativo;
- autenticacion reforzada para roles con acceso a multiples clientes;
- consulta de cumplimiento por actores terceros autorizados;
- comparacion historica entre periodos para facilitar auditoria y toma de decisiones.
