document.addEventListener('DOMContentLoaded', () => {
    console.log(' informe.js cargado - Intentando cargar datos del informe.');

    // Carga los datos del informe desde localStorage
    const informeSolarString = localStorage.getItem('informeSolar');
    let datos = null;

    if (informeSolarString) {
        try {
            datos = JSON.parse(informeSolarString);
            console.log('Datos del informe cargados exitosamente:', datos);
        } catch (e) {
            console.error('Error al parsear el JSON del informe desde localStorage:', e);
            // En caso de error, limpia el localStorage para evitar problemas futuros
            localStorage.removeItem('informeSolar');
            alert('Hubo un problema al cargar el informe. Por favor, vuelva a realizar el cálculo.');
            window.location.href = 'calculador.html'; // Redirige al calculador
            return; // Detiene la ejecución
        }
    }

    // Si no hay datos, muestra un mensaje o redirige
    if (!datos) {
        console.warn('No se encontraron datos de informe en localStorage.');
        document.querySelector('.solar-report').innerHTML = `
            <div class="report-title">
                Informe de Viabilidad de Instalación Solar Fotovoltaica
            </div>
            <p style="text-align: center; padding: 20px; font-size: 1.1rem;">
                No se ha encontrado ningún informe. Por favor, complete el <a href="calculador.html">formulario de cálculo</a> para generar uno.
            </p>
            <div class="informe-btns">
                <button class="informe-btn" onclick="window.location.href='calculador.html'">Volver al Calculador</button>
            </div>
        `;
        return; // Detiene la ejecución si no hay datos
    }

    // Función auxiliar para poblar elementos (si aún se necesita para otros campos)
    function setTextContent(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        } else {
            console.warn(`Elemento con ID '${id}' no encontrado.`);
        }
    }

    // --- NUEVA FUNCIÓN PARA POBLAR EL REPORTE DINÁMICO ---
    function poblarReporteBasico(reporteData) {
        const tbody = document.getElementById('reporte-basico-body');
        if (!tbody) {
            console.error("El cuerpo de la tabla con ID 'reporte-basico-body' no fue encontrado.");
            return;
        }
        tbody.innerHTML = ''; // Limpiar cualquier contenido existente

        reporteData.forEach(item => {
            const tr = document.createElement('tr');

            const tdDescripcion = document.createElement('td');
            tdDescripcion.textContent = item.descripcion;

            const tdValor = document.createElement('td');
            // Formatear el valor si es un número, de lo contrario mostrarlo como está
            let valorMostrado = item.valor;
            const valorNumerico = parseFloat(item.valor);
            if (!isNaN(valorNumerico)) {
                // Formatear a 2 decimales si es un número flotante
                valorMostrado = Number.isInteger(valorNumerico) ? valorNumerico.toString() : valorNumerico.toFixed(2);
            }

            tdValor.textContent = `${valorMostrado} ${item.unidad || ''}`.trim();
            tdValor.style.textAlign = 'right'; // Alinear valor a la derecha para mejor legibilidad

            tr.appendChild(tdDescripcion);
            tr.appendChild(tdValor);
            tbody.appendChild(tr);
        });
    }

    // Poblar los datos del informe en el HTML
    // Mantener los campos que siguen existiendo, como el resumen general y la contribución climática
    setTextContent('consumo-anual', datos.consumo_anual?.toFixed(2) || 'N/A');
    // Los siguientes campos ya no existen en el HTML, por lo que se pueden eliminar o comentar
    // setTextContent('generacion-anual', datos.generacion_anual?.toFixed(2) || 'N/A');
    // setTextContent('autoconsumo', datos.autoconsumo?.toFixed(2) || 'N/A');
    // setTextContent('inyectada-red', datos.inyectada_red?.toFixed(2) || 'N/A');

    // Llamar a la nueva función para poblar la tabla dinámica
    if (datos.reporte_basico && Array.isArray(datos.reporte_basico)) {
        poblarReporteBasico(datos.reporte_basico);
    } else {
        console.warn('No se encontró el array "reporte_basico" en los datos del informe.');
    }

    // Contribución al Cambio Climático (si todavía existe esta sección)
    // Suponiendo que 'emisiones' es un valor que quieres mostrar y que la sección existe
    // Si 'emisiones' ahora viene dentro de 'reporte_basico', esta línea ya no es necesaria.
    // Si es un campo separado, puedes mantenerlo. Por ahora lo comento.
    // setTextContent('emisiones', datos.emisiones?.toFixed(2) || 'N/A');


    // Descargar PDF con html2pdf.js
    document.getElementById('descargarPDF')?.addEventListener('click', function() {
        const element = document.querySelector('.solar-report');
        const opt = {
            margin: 0.5,
            filename: 'informe_solar.pdf',
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2, logging: true, dpi: 192, letterRendering: true },
            jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
        };
        html2pdf().set(opt).from(element).save();
    });
});