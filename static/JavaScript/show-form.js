const btnEliminar = document.querySelectorAll(".eliminar");

    btnEliminar.forEach((eliminar, index) => {
        const containerEliminar = document.querySelectorAll(".container-delete")[index];
        const containerShow = document.querySelectorAll(".show-container")[index]; 
        const btnCancelar = containerEliminar.querySelector(".cancelar");
        const btnDelete = containerEliminar.querySelector(".confirm-eliminar");

        let tiempo = 5;
        let intervalo;

        eliminar.addEventListener("click", function() {
            containerEliminar.style.display = "flex";
            containerShow.style.display = "flex";

            btnDelete.disabled = true; 
            btnDelete.textContent = `Eliminar en ${tiempo}s`;

            intervalo = setInterval(() => {
                if (tiempo > 0) {
                    tiempo--;
                    btnDelete.textContent = `Eliminar en ${tiempo}s`;
                } else {
                    clearInterval(intervalo);
                    btnDelete.disabled = false;
                    btnDelete.textContent = "Eliminar Usuario";
                }
            }, 1000);
        });

        btnCancelar.addEventListener("click", function() {
            containerEliminar.style.display = "none";
            containerShow.style.display = "none"; 
            clearInterval(intervalo);
            btnDelete.disabled = true;
            tiempo = 5;
            btnDelete.textContent = `Eliminar en ${tiempo}s`;
        });
    });



const privilegios = document.querySelectorAll(".privilegios");

privilegios.forEach(element => {
    if (element.textContent.trim() === "Permitir") {
        element.style.color = "green";
        element.style.textDecoration = "underline";
    } else {
        element.style.color = "red";
        element.style.textDecoration = "underline";
    }
});
