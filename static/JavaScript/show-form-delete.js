const btnEliminar = document.querySelectorAll(".eliminar"); 

btnEliminar.forEach((eliminar, index) => {
    const form = document.querySelectorAll(".delete-activo")[index];
    const btnCancelar = form.querySelector(".cancelar");
    const overlay = document.querySelectorAll(".overlay")[index];

    eliminar.addEventListener("click", function() {
        form.style.display = "flex"; 
        overlay.style.display = "block"; 
        btnCancelar.style.display = "block"; 
    });

    btnCancelar.addEventListener("click", function() {
        form.style.display = "none";
        overlay.style.display = "none"; 
    });
    overlay.addEventListener("click", function() {
        form.style.display = "none";
        overlay.style.display = "none"; 
    });
});