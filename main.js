document.addEventListener("DOMContentLoaded", function () {
    // Bloquear scroll en toda la página (pantalla fija)
    document.body.style.overflow = 'hidden';

    // Elementos de la pantalla inicial
    const containerInicial = document.getElementById("container-inicial");
    const input = document.getElementById("textoInput");
    const error = document.getElementById("errorMessage");
    const spinner = document.getElementById("spinner");

    // Elementos de la pantalla de resultados
    const containerResultados = document.getElementById("container-resultados");
    const resultSectionCodesList = document.getElementById("codes-list");
    const textoPlaceholder = document.getElementById("texto-placeholder");
    const newSearchBtn = document.getElementById("new-search-btn");
    const noCodesMsg = document.getElementById("no-codes-message");

    // NUEVO: almacenar sessionId para usarlo en /select
    let currentsessionId = null;

    // Quita la barra final para evitar doble barra en las rutas
    const API_BASE = "https://ffljaqyibd.execute-api.us-east-1.amazonaws.com";

    if ("visualViewport" in window) {
        window.visualViewport.addEventListener("resize", () => {
            input.scrollIntoView({ behavior: "smooth", block: "center" });
        });
    }

    function showError(message) {
        error.textContent = message;
        error.style.display = "block";
    }

    function hideMessages() {
        error.style.display = "none";
        noCodesMsg.style.display = "none";
    }

    function showSpinner() {
        spinner.style.display = "block";
    }

    function hideSpinner() {
        spinner.style.display = "none";
    }

    function renderCodes(codes) {
        resultSectionCodesList.innerHTML = "";
        if (!codes || codes.length === 0) {
            noCodesMsg.style.display = "block";
            return;
        }
        noCodesMsg.style.display = "none";
        codes.forEach(code => {
            const codeItem = document.createElement("div");
            codeItem.className = "code-item";
            const info = document.createElement("div");
            info.className = "code-info";
            const number = document.createElement("div");
            number.className = "code-number";
            number.textContent = code.codigo || code.code || "";
            const desc = document.createElement("div");
            desc.className = "code-description";
            desc.textContent = code.desc || code.descripcion || code.description || "";
            info.appendChild(number);
            info.appendChild(desc);

            const btn = document.createElement("button");
            btn.className = "select-button";
            btn.textContent = "Elegir";
            btn.onclick = function () {
                seleccionarCodigo(code);
            };

            codeItem.appendChild(info);
            codeItem.appendChild(btn);
            resultSectionCodesList.appendChild(codeItem);
        });
    }

    // Función para mostrar toast emergente de éxito
    function showSuccessToast(message) {
        let toast = document.getElementById('success-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'success-toast';
            document.body.appendChild(toast);
        }
        toast.innerText = message;

        // Estilos amigables, centrado, verde #229954
        toast.style.position = 'fixed';
        toast.style.top = '50%';
        toast.style.left = '50%';
        toast.style.transform = 'translate(-50%, -50%)';
        toast.style.background = '#229954';
        toast.style.color = '#fff';
        toast.style.padding = '1.5em 2.5em';
        toast.style.borderRadius = '10px';
        toast.style.fontSize = '1.2em';
        toast.style.boxShadow = '0 2px 8px rgba(0,0,0,0.23)';
        toast.style.zIndex = 9999;
        toast.style.textAlign = 'center';
        toast.style.opacity = 1;
        toast.style.transition = 'opacity 0.5s';

        setTimeout(() => {
            toast.style.opacity = 0;
            setTimeout(() => {
                toast.remove();
                // Redirige y limpia el historial
                history.replaceState(null, "", "/");
                window.location.replace("https://nhug.ai");
            }, 500);
        }, 1500); // 1,5 segundos visible
    }

    async function seleccionarCodigo(code) {
        showSpinner();
        try {
            const res = await fetch(API_BASE + "/select", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    sessionId: currentsessionId,
                    codigo: code.codigo || code.code,
                    desc: code.desc || code.descripcion || code.description || ""
                })
            });
            hideSpinner();
            const data = await res.json();
            if (data && data.ok) {
                showSuccessToast("Se grabó con éxito su elección");
                // La redirección se maneja dentro de showSuccessToast
            } else {
                showError("No se pudo registrar la selección.");
            }
        } catch {
            hideSpinner();
            showError("Error al conectar con el servidor.");
        }
    }

    input.addEventListener("input", () => {
        if (input.value.trim()) hideMessages();
    });

    // Usamos keydown, pero solo actúa si hay texto no vacío
    input.addEventListener("keydown", async (e) => {
        if (e.key !== "Enter") return;
        e.preventDefault();
        const texto = input.value.trim().substring(0, 200);

        if (!texto) {
            input.focus();
            return;
        }
        hideMessages();
        showSpinner();

        try {
            const res = await fetch(API_BASE + "/texto", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ texto }) // <- SIEMPRE "texto"
            });
            hideSpinner();
            if (!res.ok) {
                const errorText = await res.text();
                throw new Error(`Error del servidor: ${res.status} ${errorText}`);
            }
            const data = await res.json();
            containerInicial.style.display = "none";
            containerResultados.style.display = "flex";
            history.replaceState(null, "", "/");
            textoPlaceholder.textContent = texto;
            renderCodes(data.codigos || data.codes || []);
            currentsessionId = data.sessionId || null;
        } catch (err) {
            hideSpinner();
            showError("Error: " + (err.message || "Error desconocido"));
        }
    });

    newSearchBtn.addEventListener("click", () => {
        containerInicial.style.display = "flex";
        containerResultados.style.display = "none";
        history.replaceState(null, "", "/");
        input.value = "";
        hideMessages();
        currentsessionId = null;
        setTimeout(() => {
            input.focus();
        }, 100);
    });

    // Inicializar
    hideMessages();
    containerInicial.style.display = "flex";
    containerResultados.style.display = "none";
    input.focus();
});
