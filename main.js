document.addEventListener("DOMContentLoaded", function () {
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

    let currentsessionId = null;
    const API_BASE = "https://ffljaqyibd.execute-api.us-east-1.amazonaws.com";

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

    // Renderiza los códigos y aplica gestión de activo por foco/hover
    function renderCodes(codes) {
        resultSectionCodesList.innerHTML = "";
        if (!codes || codes.length === 0) {
            noCodesMsg.style.display = "block";
            return;
        }
        noCodesMsg.style.display = "none";

        codes.forEach((code) => {
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

            // Solo un item activo a la vez (foco/hover)
            btn.addEventListener("focus", () => {
                document.querySelectorAll(".code-item.activo").forEach(el => el.classList.remove("activo"));
                codeItem.classList.add("activo");
            });
            btn.addEventListener("mouseenter", () => {
                document.querySelectorAll(".code-item.activo").forEach(el => el.classList.remove("activo"));
                codeItem.classList.add("activo");
            });
            btn.addEventListener("blur", () => {
                codeItem.classList.remove("activo");
            });
            btn.addEventListener("mouseleave", () => {
                codeItem.classList.remove("activo");
            });

            codeItem.appendChild(info);
            codeItem.appendChild(btn);
            resultSectionCodesList.appendChild(codeItem);
        });
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
            } else {
                showError("No se pudo registrar la selección.");
            }
        } catch {
            hideSpinner();
            showError("Error al conectar con el servidor.");
        }
    }

    function showSuccessToast(message) {
        let toast = document.getElementById('success-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'success-toast';
            document.body.appendChild(toast);
        }
        toast.innerText = message;
        toast.style.position = 'fixed';
        toast.style.top = '50%';
        toast.style.left = '50%';
        toast.style.transform = 'translate(-50%, -50%)';
        toast.style.background = '#317f43';
        toast.style.padding = '1.5em 2.5em';
        toast.style.borderRadius = '10px';
        toast.style.fontSize = 'clamp(15px, 3vw, 22px)';
        toast.style.boxShadow = '0 2px 8px rgba(0,0,0,0.23)';
        toast.style.zIndex = 9999;
        toast.style.textAlign = 'center';
        toast.style.color = '#fff';
        toast.style.opacity = 1;
        toast.style.fontFamily = 'monospace';
        toast.style.fontWeight = 'bold';
        toast.style.transition = 'opacity 0.5s';

        setTimeout(() => {
            toast.style.opacity = 0;
            setTimeout(() => {
                toast.remove();
                // Cierre de ventana por JS, solo si fue abierta por window.open
                if (window.opener) {
                    window.close();
                } else {
                    // Si no, simplemente recarga para volver al inicio
                    location.reload();
                }
            }, 500);
        }, 2000);
    }

    // Entrada principal: Intro en caja texto
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
                body: JSON.stringify({ texto })
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
            renderCodes(data.codigos || data.codes || data.candidatos_gpt || []);
            currentsessionId = data.sessionId || null;
        } catch (err) {
            hideSpinner();
            showError("Error: " + (err.message || "Error desconocido"));
        }
    });

    // Nuevo intento
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

    // Inicialización
    hideMessages();
    containerInicial.style.display = "flex";
    containerResultados.style.display = "none";
    input.focus();
});
