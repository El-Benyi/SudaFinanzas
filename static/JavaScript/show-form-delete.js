const btnEliminar = document.querySelectorAll(".eliminar"); 

btnEliminar.forEach((eliminar, index) => {
    const form = document.querySelectorAll(".delete-activo")[index];
    const btnCancelar = form.querySelector(".cancelar"); // Encuentra el botón cancelar dentro del formulario

    eliminar.addEventListener("click", function() {
        form.style.display = "flex"; 
        btnCancelar.style.display = "block"; 
    });

    btnCancelar.addEventListener("click", function() {
        form.style.display = "none";
    });
});