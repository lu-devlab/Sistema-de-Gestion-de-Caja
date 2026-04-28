const cajaPulso = (() => {
    const graficos = {};

    function iniciar() {
        actualizarDatosGraficos(document);
        activarAlertas(document);
        activarToasts(document);
        activarValidaciones(document);
        activarFiltros(document);
        activarExportacionPdf(document);
        activarAccionesAsync(document);
        activarGraficos();
        activarDropdown(document);
    }

    function activarAlertas(root) {
        const mensajes = root.querySelectorAll('.mensaje-estado');

        mensajes.forEach((mensaje) => {
            mensaje.classList.add('mensaje-visible');

            window.setTimeout(() => {
                mensaje.classList.remove('mensaje-visible');
                mensaje.classList.add('mensaje-oculto');
            }, 3200);
        });
    }

    function activarToasts(root) {
        const contenedor = root.querySelector('[data-toast-root]');

        if (!contenedor) {
            return;
        }

        posicionarToasts(root);
        const toasts = contenedor.querySelectorAll('[data-toast]');

        toasts.forEach((toast, indice) => {
            if (toast.dataset.toastActivo === 'si') {
                return;
            }

            toast.textContent = toast.textContent.trim().replace(/\.$/, '');
            toast.dataset.toastActivo = 'si';

            window.requestAnimationFrame(() => {
                toast.classList.add('is-visible');
            });

            window.setTimeout(() => {
                ocultarToast(toast);
            }, 1700 + (indice * 140));
        });
    }

    function obtenerAnclaToast(root) {
        const selectores = [
            '.acciones-formulario .btn-guardar',
            '.acciones-formulario .btn-apertura',
            '.acciones-formulario button[type="submit"]',
            '.form-footer-box .btn-guardar',
            '.form-footer-box button[type="submit"]',
            '.login-right .login-btn',
            'form button[type="submit"]',
        ];

        for (const selector of selectores) {
            const ancla = root.querySelector(selector);
            if (ancla) {
                return ancla;
            }
        }

        return null;
    }

    function posicionarToasts(root) {
        const contenedor = document.querySelector('[data-toast-root]');

        if (!contenedor) {
            return;
        }

        const ancla = obtenerAnclaToast(root);

        if (!ancla) {
            contenedor.classList.remove('is-anchored');
            contenedor.style.removeProperty('--toast-left');
            contenedor.style.removeProperty('--toast-top');
            return;
        }

        const rect = ancla.getBoundingClientRect();
        const margen = 12;
        const anchoEstimado = Math.min(window.innerWidth - (margen * 2), 420);
        const mitad = anchoEstimado / 2;
        const centro = rect.left + (rect.width / 2);
        const left = Math.min(
            window.innerWidth - mitad - margen,
            Math.max(mitad + margen, centro),
        );
        const top = Math.max(20, rect.top - 14);

        contenedor.classList.add('is-anchored');
        contenedor.style.setProperty('--toast-left', `${left}px`);
        contenedor.style.setProperty('--toast-top', `${top}px`);
    }

    function reposicionarToasts() {
        posicionarToasts(document);
    }

    function ocultarToast(toast) {
        if (!toast || toast.dataset.toastOcultando === 'si') {
            return;
        }

        toast.dataset.toastOcultando = 'si';
        toast.classList.remove('is-visible');
        toast.classList.add('is-hiding');

        window.setTimeout(() => {
            const contenedor = toast.closest('[data-toast-root]');
            toast.remove();

            if (contenedor && !contenedor.querySelector('[data-toast]')) {
                contenedor.innerHTML = '';
            }
        }, 240);
    }

    function sincronizarToasts(doc) {
        const contenedorActual = document.querySelector('[data-toast-root]');
        const nuevoContenedor = doc.querySelector('[data-toast-root]');

        if (!contenedorActual || !nuevoContenedor) {
            return;
        }

        contenedorActual.innerHTML = nuevoContenedor.innerHTML;
        activarToasts(document);
    }

    function sincronizarCampanaNotificaciones(doc) {
        const campanaActual = document.querySelector('[data-notification-bell]');
        const campanaNueva = doc.querySelector('[data-notification-bell]');

        if (!campanaActual || !campanaNueva) {
            return;
        }

        campanaActual.outerHTML = campanaNueva.outerHTML;
    }

    function activarValidaciones(root) {
        const campos = root.querySelectorAll(
            'input, select, textarea',
        );

        campos.forEach((campo) => {
            campo.addEventListener('input', () => validarCampo(campo));
            campo.addEventListener('blur', () => validarCampo(campo));
        });
    }

    function validarCampo(campo) {
        if (campo.disabled || campo.type === 'hidden') {
            return;
        }

        const valor = campo.value.trim();
        let valido = true;
        let mensaje = '';

        if (campo.required && !valor) {
            valido = false;
            mensaje = 'Este campo es obligatorio';
        }

        if (
            valido &&
            campo.type === 'number' &&
            valor
        ) {
            const numero = Number(valor);
            const minimo = campo.min ? Number(campo.min) : null;

            if (Number.isNaN(numero)) {
                valido = false;
                mensaje = 'Ingrese un numero valido';
            } else if (minimo !== null && numero < minimo) {
                valido = false;
                mensaje = `El valor minimo es ${campo.min}`;
            }
        }

        campo.setCustomValidity(mensaje);
        campo.classList.toggle('campo-error', !valido);
        campo.classList.toggle('campo-ok', valido && !!valor);
    }

    function activarFiltros(root) {
        const periodo = root.querySelector('#periodo');
        const fecha = root.querySelector('#fecha');
        const desde = root.querySelector('#desde');
        const hasta = root.querySelector('#hasta');

        if (!periodo || !fecha || !desde || !hasta) {
            return;
        }

        const actualizar = () => {
            const esRango = periodo.value === 'rango';
            const bloqueFecha = fecha.closest('.filtro-bloque');
            const bloqueDesde = desde.closest('.filtro-bloque');
            const bloqueHasta = hasta.closest('.filtro-bloque');

            bloqueFecha.hidden = esRango;
            bloqueDesde.hidden = !esRango;
            bloqueHasta.hidden = !esRango;

            fecha.disabled = esRango;
            desde.disabled = !esRango;
            hasta.disabled = !esRango;
        };

        periodo.addEventListener('change', actualizar);
        actualizar();
    }

    function activarAccionesAsync(root) {
        const formularios = root.querySelectorAll('[data-async="si"]');
        const enlaces = root.querySelectorAll('[data-async-link="si"]');

        formularios.forEach((formulario) => {
            if (formulario.dataset.asyncActivo === 'si') {
                return;
            }

            formulario.dataset.asyncActivo = 'si';
            formulario.addEventListener('submit', manejarFormularioAsync);
        });

        enlaces.forEach((enlace) => {
            if (enlace.dataset.asyncActivo === 'si') {
                return;
            }

            enlace.dataset.asyncActivo = 'si';
            enlace.addEventListener('click', manejarEnlaceAsync);
        });
    }

    function activarExportacionPdf(root) {
        const botones = root.querySelectorAll('[data-exportar-pdf="si"]');

        botones.forEach((boton) => {
            if (boton.dataset.pdfActivo === 'si') {
                return;
            }

            boton.dataset.pdfActivo = 'si';
            boton.addEventListener('click', () => {
                window.print();
            });
        });
    }

    function activarDropdown(root) {
        const btn = root.querySelector('#btn-configuracion');
        const dropdown = root.querySelector('#dropdown-config');

        if (!btn || !dropdown) return;

        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdown.classList.toggle('active');
        });

        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target) && e.target !== btn) {
                dropdown.classList.remove('active');
            }
        });
    }

    async function manejarFormularioAsync(evento) {
        evento.preventDefault();
        const formulario = evento.currentTarget;
        const metodo = (formulario.method || 'get').toUpperCase();
        const accion = formulario.getAttribute('action')
            || window.location.pathname;
        const datos = new FormData(formulario);
        const opciones = {
            method: metodo,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        };

        let url = accion;

        if (metodo === 'GET') {
            const consulta = new URLSearchParams(datos).toString();
            url = consulta ? `${accion}?${consulta}` : accion;
        } else {
            opciones.body = datos;
        }

        await cargarContenido(url, opciones);
    }

    async function manejarEnlaceAsync(evento) {
        evento.preventDefault();
        const enlace = evento.currentTarget;
        await cargarContenido(enlace.href, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        });
    }

    async function cargarContenido(url, opciones) {
        try {
            const respuesta = await fetch(url, opciones);
            const html = await respuesta.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const nuevoContenido = doc.querySelector('.content-body');
            const contenidoActual = document.querySelector('.content-body');
            const destinoUrl = new URL(
                respuesta.url || url,
                window.location.origin,
            );
            const hashDestino = destinoUrl.hash;

            if (!nuevoContenido || !contenidoActual) {
                window.location.assign(respuesta.url || url);
                return;
            }

            actualizarDatosGraficos(doc);
            contenidoActual.replaceWith(nuevoContenido);
            sincronizarToasts(doc);
            sincronizarCampanaNotificaciones(doc);
            document.title = doc.title || document.title;
            history.replaceState({}, '', destinoUrl.pathname);
            destruirGraficos();
            activarAlertas(document);
            activarToasts(document);
            activarValidaciones(document);
            activarFiltros(document);
            activarExportacionPdf(document);
            activarAccionesAsync(document);
            activarGraficos();
            desplazarAHash(hashDestino);
        } catch (error) {
            window.location.assign(url);
        }
    }

    function desplazarAHash(hashDestino = '') {
        if (!hashDestino) {
            const contenido = document.querySelector('.content-body');
            if (contenido) {
                contenido.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start',
                });
            }
            return;
        }

        const destino = document.querySelector(hashDestino);
        if (destino) {
            destino.scrollIntoView({
                behavior: 'smooth',
                block: 'start',
            });
        }
    }

    function activarGraficos() {
        if (typeof Chart === 'undefined') {
            return;
        }

        const datos = window.cajaPulsoGraficos;

        if (!datos) {
            return;
        }

        crearGraficoLinea(datos);
        crearGraficoEstado(datos);
    }

    function actualizarDatosGraficos(doc) {
        const fechas = doc.querySelector('#grafico-fechas');
        const ingresos = doc.querySelector('#grafico-ingresos');
        const egresos = doc.querySelector('#grafico-egresos');
        const saldos = doc.querySelector('#grafico-saldos');
        const estados = doc.querySelector('#grafico-estados');

        if (!fechas || !ingresos || !egresos || !saldos || !estados) {
            window.cajaPulsoGraficos = null;
            return;
        }

        window.cajaPulsoGraficos = {
            fechas: JSON.parse(fechas.textContent),
            ingresos: JSON.parse(ingresos.textContent),
            egresos: JSON.parse(egresos.textContent),
            saldos: JSON.parse(saldos.textContent),
            estados: JSON.parse(estados.textContent),
        };
    }

    function destruirGraficos() {
        Object.values(graficos).forEach((grafico) => {
            if (grafico) {
                grafico.destroy();
            }
        });
    }

    function crearGraficoLinea(datos) {
        const canvas = document.querySelector('#grafico-periodo');

        if (!canvas) {
            return;
        }

        graficos.periodo = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: datos.fechas,
                datasets: [
                    {
                        label: 'Ingresos',
                        data: datos.ingresos,
                        borderColor: '#1f8a5b',
                        backgroundColor: 'rgba(31, 138, 91, 0.12)',
                        borderRadius: 10,
                        borderSkipped: false,
                    },
                    {
                        label: 'Egresos',
                        data: datos.egresos,
                        borderColor: '#d46464',
                        backgroundColor: 'rgba(212, 100, 100, 0.74)',
                        borderRadius: 10,
                        borderSkipped: false,
                    },
                    {
                        label: 'Saldo neto',
                        data: datos.saldos,
                        borderColor: '#245d4a',
                        backgroundColor: 'rgba(36, 93, 74, 0.74)',
                        borderRadius: 10,
                        borderSkipped: false,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                    },
                },
            },
        });
    }

    function crearGraficoEstado(datos) {
        const canvas = document.querySelector('#grafico-cierres');

        if (!canvas) {
            return;
        }

        const porcentajePlugin = {
            id: 'porcentajePlugin',
            afterDatasetsDraw(chart) {
                const { ctx } = chart;
                const dataset = chart.data.datasets[0];
                const total = dataset.data.reduce(
                    (acumulado, valor) => acumulado + valor,
                    0,
                );

                if (!total) {
                    return;
                }

                chart.getDatasetMeta(0).data.forEach((arco, indice) => {
                    const valor = dataset.data[indice];

                    if (!valor) {
                        return;
                    }

                    const porcentaje = Math.round((valor / total) * 100);
                    const posicion = arco.tooltipPosition();

                    ctx.save();
                    ctx.fillStyle = '#113426';
                    ctx.font = '700 12px Inter';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(
                        `${porcentaje}%`,
                        posicion.x,
                        posicion.y,
                    );
                    ctx.restore();
                });
            },
        };

        graficos.cierres = new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: construirEtiquetasEstado(datos.estados),
                datasets: [
                    {
                        data: datos.estados,
                        backgroundColor: [
                            '#2a8c61',
                            '#df7d4a',
                            '#4d9ab7',
                        ],
                        borderWidth: 0,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '58%',
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                },
            },
            plugins: [porcentajePlugin],
        });
    }

    function construirEtiquetasEstado(estados) {
        const nombres = ['Cuadrada', 'Faltante', 'Sobrante'];
        const total = estados.reduce(
            (acumulado, valor) => acumulado + valor,
            0,
        );

        return nombres.map((nombre, indice) => {
            const valor = estados[indice];
            const porcentaje = total
                ? Math.round((valor / total) * 100)
                : 0;

            return `${nombre} ${porcentaje}%`;
        });
    }

    function reactivarGraficos() {
        destruirGraficos();
        activarGraficos();
    }

    return { iniciar, reactivarGraficos, reposicionarToasts };
})();

document.addEventListener('DOMContentLoaded', cajaPulso.iniciar);
window.addEventListener('load', cajaPulso.reactivarGraficos);
window.addEventListener('resize', cajaPulso.reposicionarToasts);
