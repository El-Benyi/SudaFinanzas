var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('actualizar_saldo', function(data) {
    console.log(data);

    if (data.saldo !== undefined) {
        document.getElementById('saldo-disponible').textContent = '$' + data.saldo;
    }
});