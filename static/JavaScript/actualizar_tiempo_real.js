const deleteBtn = document.querySelectorAll(".eliminar")
const btnConfirmar = document.getElementById("btnConfirmar")



deleteBtn.forEach((btnEliminar, index) => {
    const formShow = document.querySelectorAll(".deleteForm")[index];
    const overlay = document.querySelectorAll(".overlay-show")[index];
    const cancelarBtn = document.querySelectorAll(".cancelar-delete")[index];

    btnEliminar.addEventListener("click", function(){
        formShow.style.display = "flex"
        overlay.style.display = "block"

        //* Logica de temporizador

        let cuentaAtras = 5;

        let intervalo = setInterval(() => {
            btnConfirmar.innerHTML = `Confirmar Eliminación en ${cuentaAtras} <ion-icon name="alert-circle-outline"></ion-icon>`;
            cuentaAtras--;

            if (cuentaAtras < 0) {
                clearInterval(intervalo); 
                btnConfirmar.disabled = false; 
            }
        }, 1000); 
    });

    cancelarBtn.addEventListener("click", function(){
        formShow.style.display = "none"
        overlay.style.display = "none"
        btnConfirmar.disabled = true; 
    });
    overlay.addEventListener("click", function(){
        formShow.style.display = "none"
        overlay.style.display = "none"
        btnConfirmar.disabled = true; 
    });
        
    
});







