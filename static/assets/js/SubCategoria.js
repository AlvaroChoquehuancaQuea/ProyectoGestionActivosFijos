var table;

init();

//FUNCION QUE SE EJECUTARA AL INICIO
function init()
{
    LlenarTablaSubCategoria();
    
}

$('#btn_add_subcategoria').on("click",function(){
    ListarCategoriasSelect();
});

//FUNCION PARA LLENAR LA TABLA SUBCATEGORIA
function LlenarTablaSubCategoria()
{
    table = $('#table_subcategoria').DataTable({
        pageLength: 10,
        responsive: true,
        processing: true,
        ajax: "../controller/SubCategoriaController.php?operador=listar_subcategorias",
        columns : [
            { data : 'op'},
            { data : 'id'},
            { data : 'nombre'},
            { data : 'categoria'},
            { data : 'estado'},
        ]
        
    });
}

//FUNCION PARA OBTENER DATOS DE UNA SUBCATEGORIA POR ID
function ObtenerSubCategoriaPorId(subcategoria_id,op)
{
    $.ajax({
        data: { "subcategoria_id":subcategoria_id },
        url:'../controller/SubCategoriaController.php?operador=obtener_subcategoria_por_id',
        type:'POST',
        beforeSend:function(){},
        success:function(response){
            data = $.parseJSON(response);
            if(data.length >0 ){
                if(op == "editar"){
                    $('#nombre_subcat_edit').val(data[0]["nombre"]);
                    ListarCategoriasSelectEdit(data[0]["subcategoria_id"]);
                }
            }
        }
    });
}

//FUNCION PARA LLENAR EL SELECT DE CATEGORIAS
function ListarCategoriasSelect()
{
    $.ajax({
        url:'../controller/CategoriaController.php?operador=listar_categorias_select',
        type:'GET',
        beforeSend:function(){},
        success:function(respuesta){
            data = $.parseJSON(respuesta);
            if(data.length > 0){
                select = "<option>SELECCIONAR UNA CATEGORIA..</option>";
                $.each(data,function(key, value){
                    select = select + "<option value="+value[0]+">"+value[1]+"</option>";
                })
                $('#categoria_perteneciente').html(select);
            }
        }
    });
}

//FUNCION PARA LLENAR EL SELECT DE CATEGORIAS PARA EDITAR
function ListarCategoriasSelectEdit(subcategoria_id)
{
    $.ajax({
        data: { "subcategoria_id":subcategoria_id },
        url:'../controller/CategoriaController.php?operador=listar_categorias_select_edit',
        type:'POST',
        beforeSend:function(){},
        success:function(respuesta){
            data = $.parseJSON(respuesta);
            if(data.length > 0){
                select = "";
                $.each(data,function(key, value){
                    select = select + "<option value="+value[0]+">"+value[1]+"</option>";
                })
                $('#categoria_perteneciente_edit').html(select);
            }
        }
    });
}





/*============================ | CRUD | ============================*/

    //FUNCION PARA REGISTRAR SUBCATEGORIA
    function RegistrarSubCategoria()
    {
        nombre = $('#nombre_subcat').val();
        categoria_id = $('#categoria_perteneciente').val();
        parametros = {
            "nombre":nombre,"categoria_id":categoria_id
        }
        $.ajax({
            data:parametros,
            url:'../controller/SubCategoriaController.php?operador=registrar_subcategoria',
            type:'POST',
            beforeSend:function(){},
            success:function(response){
                if(response == "success"){
                    table.ajax.reload();
                    toastr.success('Se guardo correctamente los datos','Registro Exitoso!');
                    $('#create_subcategoria').modal('hide');
                } else if (response == "requerid") {
                    toastr.error('Por favor rellene todos los  campos','Campos imcompletos!');
                } else {
                    toastr.error('Comuniquese con su proveedor','Error inesperado!');
                }
            }
        });
    }
