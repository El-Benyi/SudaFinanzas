document.addEventListener("DOMContentLoaded", function() {
    const today = new Date(); 
    const day = String(today.getDate()).padStart(2, '0'); 
    const month = String(today.getMonth() + 1).padStart(2, '0'); 
    const year = today.getFullYear(); 

    const formattedDate = `${year}-${month}-${day}`; 

  
    const fechaInput = document.getElementById("fecha");
    fechaInput.setAttribute("max", formattedDate); 
});
