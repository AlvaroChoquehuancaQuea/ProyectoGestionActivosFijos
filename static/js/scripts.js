function confirmarEliminacion(elemento) {
    Swal.fire({
        title: '¿Estás seguro?',
        text: 'Esta acción no se puede deshacer.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6'
    }).then((result) => {
        if (result.isConfirmed) {
            // Redirige a la URL de eliminación
            window.location.href = elemento.getAttribute('data-url');
        }
    });
}
function limpiarCampos() {
    setTimeout(() => {
        document.getElementById('codigo').value = '';
        document.getElementById('descripcion').value = '';
        document.getElementById('fecha').value = '';
    }, 100);
}