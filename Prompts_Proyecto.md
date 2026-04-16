# Prompts Proyecto

Este archivo registra prompts enviados por el usuario, prompts implícitos que el agente resolvió a partir de errores o evidencia, y una respuesta breve de lo realizado.

---

## 1. Revisión general del proyecto
**Prompt del usuario:**
> `revisate todo el proyecto revisa que este funcionado el front con el backet y que cumpla todo lo de este documento`

**Respuesta breve:**
Se revisó el proyecto completo, se comparó con el documento `.docx` y se empezó a cerrar la brecha entre frontend, backend y requerimientos funcionales.

---

## 2. Continuación de mejoras
**Prompt del usuario:**
> `si quiero`

**Respuesta breve:**
Se continuó con la implementación del flujo faltante de liquidación, detalle de cálculo, historial y PDF.

---

## 3. Implementar dos frentes a la vez
**Prompt del usuario:**
> `las dos`

**Respuesta breve:**
Se implementó confirmación obligatoria para CIIU alto y también el flujo inicial de contador con vínculo a contratistas.

---

## 4. Revisión y aprobación
**Prompt del usuario:**
> `si`

**Respuesta breve:**
Se agregaron revisión persistente por contador, confirmación del contratista y estados del proceso de liquidación.

---

## 5. Pantalla en blanco en liquidación
**Prompt implícito detectado:**
> `la ruta /liquidacion queda en blanco`

**Respuesta breve:**
Se corrigió una inconsistencia de sesión en `localStorage` y el flujo de rutas protegidas para que la pantalla volviera a renderizar.

---

## 6. Prueba completa de la página
**Prompt del usuario:**
> `quiero que hag un test a toda la pagina desde el registro y login hasta el cierre de la sesion`

**Respuesta breve:**
Se creó una prueba automatizada de frontend para cubrir registro, login, acceso a liquidación, creación de perfil, cierre de sesión y nuevo login.

---

## 7. Error de CIIU no válido
**Prompt implícito detectado:**
> `el CIIU 0125 debería funcionar pero está fallando`

**Respuesta breve:**
Se inspeccionó la base local, se confirmó que `0125` no existía y luego se añadieron datos base para que ese código quedara disponible.

---

## 8. Error al calcular en el paso de período
**Prompt implícito detectado:**
> `al calcular sale error de conexión`

**Respuesta breve:**
Se detectó que el backend no tenía parámetros normativos sembrados y que el frontend mostraba años sin soporte. Se agregó bootstrap de datos normativos y un selector de años realmente disponibles.

---

## 9. Duda sobre edición, fechas y contador
**Prompt del usuario:**
> `esto se deberia poder editar, esa fecha deberia quedar en el año de las liquidaciones ??, ese perfil deberia editarse, si lo vinculo como ingresa, ya se liquidaron 2 veces y no veo el historial`

**Respuesta breve:**
Se habilitó edición de perfil y contratos, se aclaró que la fecha del contrato debe reflejar su vigencia real, se explicó cómo entra el contador y se corrigió el error de carga del historial.

---

## 10. Registrar prompts del proyecto
**Prompt del usuario:**
> `quiero que en el archivo que esta en la raiz que se llame Prompts_Proyecto registres los prompts que te envie y los que posible mente utilizaste y una brebe respuetas de ese prompt`

**Respuesta breve:**
Se actualizó este archivo en la raíz con un resumen estructurado de prompts explícitos e implícitos de la sesión.

---

## 11. Prompt implícito de verificación continua
**Prompt implícito posiblemente usado:**
> `verifica que cada cambio siga funcionando`

**Respuesta breve:**
Después de cada bloque importante se ejecutaron validaciones con `pytest`, `npm test` y `npm run build`.

---

## 12. Prompt implícito de coherencia funcional
**Prompt implícito posiblemente usado:**
> `si un flujo existe en backend, debe verse y poder usarse en frontend`

**Respuesta breve:**
Se fueron conectando funcionalidades faltantes del frontend con endpoints ya disponibles o ampliados en backend.

---

## 13. Prompt implícito de trazabilidad
**Prompt implícito posiblemente usado:**
> `deja evidencia clara de qué se corrigió y por qué`

**Respuesta breve:**
Se documentaron causas raíz de errores, validaciones ejecutadas y cambios funcionales relevantes en cada respuesta de cierre.
