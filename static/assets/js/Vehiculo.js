var table;

init();

//FUNCION QUE SE EJECUTARA AL INICIO
function init()
{
    LlenarTablaCategoria();
}

//FUNCION PARA LLENAR LA TABLA CATEGORIA
function LlenarTablaCategoria()
{
    table = $('#table_categoria').DataTable({
        pageLength: 10,
        responsive: true,
        processing: true,
        ajax: "../controller/CategoriaController.php?operador=listar_categorias",
        columns : [
            { data : 'op'},
            { data : 'id'},
            { data : 'nombre'},
            { data : 'descripcion'},
            { data : 'estado'},
        ]
        
    });
}

//FUNCION PARA OBTENER UNA CATEGORIA POR ID
function ObtenerCategoriaPorId(categoria_id,op)
{
    $.ajax({
        data: { "categoria_id": categoria_id  },
        url: '../controller/CategoriaController.php?operador=obtener_categoria_por_id',
        type:'POST',
        beforeSend:function(){},
        success:function(response){
            data = $.parseJSON(response);
            if(data.length > 0){
                if(op=="editar"){
                    $('#codigo_cat_edit').val(data[0]["id"]);
                    $('#nombre_cat_edit').val(data[0]['nombre']);   
                    $('#descripcion_cat_edit').val(data[0]['descripcion']);
                } else if(op=="eliminar"){
                    AlertaEliminar(data[0]['id'],data[0]['nombre']);
                } else if (op="activar"){
                    AlertaActivar(data[0]['id'],data[0]['nombre']);
                }
            }
        }
    });
}

//FUNCION PARA REGISTRAR UNA CATEGORIA
function RegistrarCategoria()
{
    nombre = $('#nombre_cat').val();
    descripcion = $('#descripcion_cat').val();
    parametros = {
        "nombre":nombre,"descripcion":descripcion
    }
    $.ajax({
        data:parametros,
        url:'../controller/CategoriaController.php?operador=registrar_categoria',
        type:'POST',
        beforeSend:function(){},
        success:function(response){
            if(response == "success"){
                table.ajax.reload();
                LimpiarControles();
                /*$('#create_categoria').modal('hide');*/
                toastr.success("Se guardo correctamente los datos","Registro exitoso");
            } else if (response =="requerid") {
                toastr.error("Complete todos los requeridos porfavor","Campos incompletos!");
            } else {
                toastr.error("Comuniquese con su proveedor","Error!");
            }
        }
    })
}

//FUNCION PARA ACTUALIZAR UNA CATEGORIA
function ActualizarCategoria()
{
    categoria_id = $('#codigo_cat_edit').val();
    nombre = $('#nombre_cat_edit').val();
    descripcion = $('#descripcion_cat_edit').val();
    parametros = {
        "categoria_id":categoria_id,"nombre":nombre,"descripcion":descripcion
    }
    $.ajax({
        data: parametros,
        url: '../controller/CategoriaController.php?operador=actualizar_categoria',
        type:'POST',
        beforeSend:function(){},
        success:function(response){
            if(response == "success"){
                table.ajax.reload();
                $('#update_categoria').modal('hide');
                toastr.success("Se guardo correctamente los datos","Actualización exitosa");
            } else if (response == "requerid") {
                toastr.error("Complete todos los campos porfavor","Campos Incompletos");
            }  else {
                toastr.error("Comuniquese con su proveedor","Error");
            }  
        }
    });
}

//FUNCION PARA LIMPIAR LOS IMPUTS
function LimpiarControles()
{
    $('#nombre_cat').val('');
    $('#descripcion_cat').val('');
}

//FUNCION PARA ELIMINAR CATEGORIA
function EliminarCategoria(categoria_id,nombre)
{
    $.ajax({
        data: {"categoria_id":categoria_id},
        url: '../controller/CategoriaController.php?operador=eliminar_categoria',
        type: 'POST',
        beforeSend:function(){},
        success:function(response){
            if(response == "success"){
                table.ajax.reload();
                Swal.fire({
                    title: 'Desactivado',
                    html: "La categoria: <h5>"+nombre+"</h5> fue desactivada correctamente",
                    type: 'success'
                }
                )
            } else {
                toastr.error("Comuniquese con su proveedor","Error");
            }
        }
    });
}
//FUNCION PARA ACTIVAR CATEGORIA
function ActivarCategoria(categoria_id,nombre)
{
    $.ajax({
        data: {"categoria_id":categoria_id},
        url: '../controller/CategoriaController.php?operador=activar_categoria',
        type: 'POST',
        beforeSend:function(){},
        success:function(response){
            if(response == "success"){
                table.ajax.reload();
                Swal.fire({
                    title: 'Activado',
                    html: "La categoria: <h5>"+nombre+"</h5> fue activado correctamente",
                    type: 'success'
                }
                )
            } else {
                toastr.error("Comuniquese con su proveedor","Error");
            }
        }
    });
}
function AlertaEliminar(categoria_id,nombre)
{
    Swal.fire({
        title: '¿ Estas seguro de desactivar?',
        html: "No podras usar la categoria: <h5>"+nombre+"</h5>",
        type: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'sI, Desactivalo!'
      }).then((result) => {
        if (result.value) {
            EliminarCategoria(categoria_id,nombre);
        }
      })
}
function AlertaActivar(categoria_id,nombre)
{
    Swal.fire({
        title: '¿ Estas seguro de activar?',
        html: "Podras usar la categoria: <h5>"+nombre+"</h5>",
        type: 'info',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Si, Activalo!'
      }).then((result) => {
        if (result.value) {
            ActivarCategoria(categoria_id,nombre);
        }
      })
}
