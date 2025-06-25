from flask import request, redirect, url_for, Blueprint, current_app, flash, send_file
from datetime import datetime
from reportlab.platypus import Image as RLImage
from models.equipo_recreativo_model import Recreativo
from views import equipo_recreativo_view
from werkzeug.utils import secure_filename
from flask_login import current_user
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import json

import numpy as np
import cv2
import pyzbar.pyzbar as pyzbar

recreativo_bp = Blueprint('recreativo', __name__, url_prefix='/recreativos')


@recreativo_bp.route('/')
def index():
    codigo = request.args.get('codigo', '').strip()
    descripcion = request.args.get('descripcion', '').strip().lower()
    fecha_str = request.args.get('fecha', '').strip()

    # Solo traer vehículos del usuario actual
    recreativos = Recreativo.query.filter_by(user_id=current_user.id).all()
    resultados = []

    for v in recreativos:
        coincide_codigo = codigo == '' or str(v.id) == codigo
        coincide_descripcion = descripcion == '' or descripcion in v.descripcion.lower()
        coincide_fecha = True

        if fecha_str:
            try:
                fecha_busqueda = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                coincide_fecha = v.fecha_incorporacion == fecha_busqueda
            except Exception:
                coincide_fecha = False

        if coincide_codigo and coincide_descripcion and coincide_fecha:
            resultados.append(v)

    return equipo_recreativo_view.list(resultados)




@recreativo_bp.route('/verificar_qr', methods=['POST'])
def verificar_qr():
    qr_file = request.files.get('qrImage')
    if not qr_file:
        flash("No se subió ningún archivo", "danger")
        return redirect(url_for('recreativo.index'))

    try:
        img_bytes = np.asarray(bytearray(qr_file.read()), dtype=np.uint8)
        img = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)

        decoded_objs = pyzbar.decode(img)

        if not decoded_objs:
            flash("No se detectó ningún código QR en la imagen", "warning")
            return redirect(url_for('recreativo.index'))

        qr_text = decoded_objs[0].data.decode('utf-8')
        datos_qr = json.loads(qr_text)

        # Extraer los 3 campos clave
        id_recreativo = datos_qr.get('id', '')
        descripcion = datos_qr.get('descripcion', '')
        fecha = datos_qr.get('fecha_incorporacion', '')

        # Redirigir con parámetros GET
        return redirect(url_for('recreativo.index', codigo=id_recreativo, descripcion=descripcion, fecha=fecha))

    except Exception as e:
        flash(f"Error al procesar la imagen QR: {str(e)}", "danger")
        return redirect(url_for('recreativo.index'))

#Creacion de recreativos
@recreativo_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        try:
            # Procesar campos del formulario
            descripcion = request.form['descripcion']
            categoria = request.form['categoria']
            modelo = request.form['modelo']
            estado = request.form['estado']
            costo_inicial = float(request.form['costo_inicial'])
            fecha_incorporacion = datetime.strptime(request.form['fecha_incorporacion'], '%Y-%m-%d').date()
            factura = float(request.form['factura'])
            años_vida_util = int(request.form['años_vida_util'])
            factor_de_actualizacion = float(request.form['factor_de_actualizacion'])
            cargo = request.form.get('cargo')
            responsable = request.form.get('responsable')

            # Procesar imagen (para creación no hay imagen previa que eliminar)
            imagen_filename = None
            if 'imagen' in request.files:
                file = request.files['imagen']
                if file.filename != '':
                    # Validar que es una imagen
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                    if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                        filename = secure_filename(file.filename)
                        upload_folder = current_app.config['UPLOAD_FOLDER']
                        
                        # Asegurar que el directorio existe
                        if not os.path.exists(upload_folder):
                            os.makedirs(upload_folder)
                        
                        file.save(os.path.join(upload_folder, filename))
                        imagen_filename = filename
                    else:
                        flash('Formato de imagen no válido. Use: .png, .jpg, .jpeg o .gif', 'danger')
                        return redirect(url_for('recreativo.create'))

            # Crear nuevo vehículo
            recreativo = Recreativo(
                descripcion=descripcion,
                categoria=categoria,
                modelo=modelo,
                estado=estado,
                costo_inicial=costo_inicial,
                fecha_incorporacion=fecha_incorporacion,
                factura=factura,
                años_vida_util=años_vida_util,
                factor_de_actualizacion=factor_de_actualizacion,
                imagen=imagen_filename,
                cargo=cargo,
                responsable=responsable,
                user_id=current_user.id
            )

            recreativo.save()
            flash('Equipo educacional recreativo creado exitosamente', 'success')
            return redirect(url_for('recreativo.index'))
            
        except Exception as e:
            current_app.logger.error(f"Error al crear Equipo Recreativo: {str(e)}")
            flash('Error al crear el Equipo Recreativo', 'danger')

    return equipo_recreativo_view.create()


#Edicion de recreativos
@recreativo_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    recreativo = Recreativo.get_by_id(id)
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        categoria = request.form['categoria']
        modelo = request.form['modelo']
        estado = request.form['estado']
        costo_inicial = float(request.form['costo_inicial'])
        fecha_incorporacion = datetime.strptime(request.form['fecha_incorporacion'], '%Y-%m-%d').date()
        factura = float(request.form['factura'])
        años_vida_util = int(request.form['años_vida_util'])
        factor_de_actualizacion = float(request.form['factor_de_actualizacion'])
        
        imagen = recreativo.imagen  # Mantener la imagen existente por defecto
        if 'imagen' in request.files:
                file = request.files['imagen']
                if file.filename != '':
                    # Eliminar la imagen anterior si existe
                    if recreativo.imagen:
                        old_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], recreativo.imagen)
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    
                    # Guardar la nueva imagen
                    filename = secure_filename(file.filename)
                    upload_folder = current_app.config['UPLOAD_FOLDER']
                    
                    # Asegurar que el directorio existe
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                    
                    file.save(os.path.join(upload_folder, filename))
                    imagen = filename

            
        cargo = request.form.get('cargo')
        responsable = request.form.get('responsable')

        recreativo.update(
            descripcion=descripcion,
            categoria=categoria,
            modelo=modelo,
            estado=estado,
            costo_inicial=costo_inicial,
            fecha_incorporacion=fecha_incorporacion,
            factura=factura,
            años_vida_util=años_vida_util,
            factor_de_actualizacion=factor_de_actualizacion,
            imagen=imagen,
            cargo=cargo,
            responsable=responsable
        )

        recreativo.save()
        return redirect(url_for('recreativo.index'))

    return equipo_recreativo_view.edit(recreativo)



@recreativo_bp.route('/imprimir')
def imprimir():
    
    try:
        
        recreativos = Recreativo.get_all()
        buffer = BytesIO()

        # Crear el documento PDF con orientación horizontal
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(letter),
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )
        
        styles = getSampleStyleSheet()
        elements = []

        # Título
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=1,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=20
        )
        title = Paragraph("REPORTE DE MAQUINAS EDUCATIVAS", title_style)
        elements.append(title)

        # Info de empresa y fecha
        info_style = ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.black,
            spaceAfter=12
        )
        fecha_str = datetime.now().strftime('%d/%m/%Y %H:%M')
        info_empresa = Paragraph("Gestion de Activos Fijos", info_style)
        info_fecha = Paragraph(f"Fecha de generación: {fecha_str}", info_style)
        elements.extend([info_empresa, info_fecha, Spacer(1, 12)])

        # Definir encabezado tabla con estilo
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.white,
            alignment=1,
            backColor=colors.HexColor('#3498db')
        )
        headers = [
            Paragraph("<b>ID</b>", header_style),
            Paragraph("<b>Descripción</b>", header_style),
            Paragraph("<b>Categoria</b>", header_style),
            Paragraph("<b>Modelo</b>", header_style),
            Paragraph("<b>Costo Inicial</b>", header_style),
            Paragraph("<b>Valor Residual</b>", header_style),
            Paragraph("<b>Vida Útil</b>", header_style),
            Paragraph("<b>Valor Neto</b>", header_style),
        ]

        data = [headers]

        # Calcular valor neto correctamente
        for v in recreativos:
            try:
                # Depreciación lineal: valor neto = costo_inicial - ((costo_inicial - factura) * años_transcurridos / años_vida_util)
                # Aquí asumimos que años_transcurridos = años_vida_util para mostrar valor neto al final de vida útil (puedes ajustar)
                valor_neto = v.costo_inicial - ((v.costo_inicial - v.factura) * (v.años_vida_util / v.años_vida_util))
                # Simplifica a factura en realidad, pero dejo fórmula
            except Exception:
                valor_neto = 0.0

            data.append([
                str(v.id),
                v.descripcion,
                v.categoria,
                v.modelo,
                f"Bs{v.costo_inicial:,.2f}",
                f"Bs{v.factura:,.2f}",
                f"{v.años_vida_util} años",
                f"Bs{valor_neto:,.2f}"
            ])

        # Configurar estilos tabla
        table = Table(data, colWidths=[0.5*inch, 2*inch, 1*inch, 1*inch, 1.2*inch, 1.2*inch, 1*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),

            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),

            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f9f9f9'), colors.white]),

            ('TEXTCOLOR', (-1, 1), (-1, -1), colors.HexColor('#e74c3c')),
            ('FONTNAME', (-1, 1), (-1, -1), 'Helvetica-Bold'),
        ]))

        elements.append(table)

        # Pie de página y firma: lo podemos hacer con callback en build()

        def add_page_number(canvas, doc):
            canvas.saveState()
            # Pie de página texto izquierdo
            canvas.setFont('Helvetica', 8)
            canvas.setFillColor(colors.HexColor('#7f8c8d'))
            canvas.drawString(inch, 0.5*inch, f"Total de Maquinas Educativas: {len(recreativos)}")

            # Pie de página texto derecho con paginación
            page_num_text = f"Página {doc.page} de {doc.pageCount if hasattr(doc, 'pageCount') else '...'}"
            canvas.drawRightString(landscape(letter)[0] - inch, 0.5*inch, page_num_text)

            # Línea firma y texto
            canvas.setStrokeColor(colors.black)
            canvas.line(inch, inch, 3*inch, inch)
            canvas.drawString(inch, 0.75*inch, "Responsable del reporte")

            canvas.restoreState()

        # Construir PDF
        doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)

        buffer.seek(0)
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"reporte_recreativos_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mimetype='application/pdf'
        )

    except Exception as e:
        current_app.logger.error(f"Error al generar reporte PDF: {str(e)}", exc_info=True)
        flash('Error al generar el reporte', 'danger')
        return redirect(url_for('recreativo.index'))
  
    
@recreativo_bp.route('/imprimir_confirmar')
def imprimir_confirmar():
    """Ruta intermedia para mostrar mensaje antes de imprimir"""
    flash("Generando reporte PDF... Por favor espere.", "info")
    return redirect(url_for('recreativo.imprimir'))  
    
# Eliminar vehículo
@recreativo_bp.route('/delete/<int:id>')
def delete(id):
    recreativo = Recreativo.get_by_id(id)
    recreativo.delete()
    return redirect(url_for('recreativo.index'))









###############################REPORTES#########################################

@recreativo_bp.route('/incorporacion')
def incorporacion():
    recreativos = Recreativo.get_all()
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )

    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=1,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20
    )
    title = Paragraph("INCORPORACIÓN Y REGISTRO DE ACTIVO FIJO EQUIPOS EDUCATIVOS", title_style)
    elements.append(title)

    fecha_str = datetime.now().strftime('%d/%m/%Y %H:%M')
    info_empresa = Paragraph("Gestion de Activos Fijos", styles['Normal'])
    info_fecha = Paragraph(f"Fecha de generación: {fecha_str}", styles['Normal'])
    elements.extend([info_empresa, info_fecha, Spacer(1, 12)])

    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.white,
        alignment=1,
        backColor=colors.HexColor('#3498db')
    )
    headers = [
        Paragraph("<b>Descripción</b>", header_style),
        Paragraph("<b>Categoria</b>", header_style),
        Paragraph("<b>Modelo</b>", header_style),
        Paragraph("<b>Estado</b>", header_style),
        Paragraph("<b>Fecha de Incorporación</b>", header_style),
        Paragraph("<b>Costo Inicial</b>", header_style),
        Paragraph("<b>Imagen</b>", header_style),
        Paragraph("<b>Años de Vida Útil</b>", header_style)
    ]
    def formatear_variable(valor):
        return f"{valor:.5f}".rstrip('0').rstrip('.')

    data = [headers]
    for v in recreativos:
        # Ruta absoluta a la imagen
        ruta_imagen = os.path.join(current_app.root_path, 'static', 'uploads', v.imagen or '')
        if v.imagen and os.path.exists(ruta_imagen):
            try:
                imagen = RLImage(ruta_imagen, width=0.8*inch, height=0.6*inch)
            except:
                imagen = Paragraph("Error al cargar", styles['Normal'])
        else:
            imagen = Paragraph("Sin imagen", styles['Normal'])

        data.append([
            v.descripcion,
            v.categoria,
            v.modelo,
            v.estado,
            v.fecha_incorporacion.strftime('%d/%m/%Y'),
            f"Bs{formatear_variable(v.costo_inicial)}",
            imagen,
            f"{v.años_vida_util} años"
        ])

    table = Table(data, colWidths=[
        1.8*inch, 1*inch, 1*inch, 1*inch,
        1.4*inch, 1.2*inch, 1*inch, 1.2*inch
    ])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f9f9f9'), colors.white])
    ]))

    elements.append(table)

    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#7f8c8d'))
        canvas.drawString(inch, 0.5*inch, f"Total  Equipos Educativos: {len(recreativos)}")
        canvas.drawRightString(landscape(letter)[0] - inch, 0.5*inch, f"Página {doc.page}")
        canvas.setStrokeColor(colors.black)
        canvas.line(inch, inch, 3*inch, inch)
        canvas.drawString(inch, 0.75*inch, "Responsable del reporte")
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="incorporacion.pdf",
        mimetype='application/pdf'
    )





@recreativo_bp.route('/financiero')
def financiero():
    recreativos = Recreativo.get_all()
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )

    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=1,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20
    )
    title = Paragraph("DETERMINACIÓN DE COSTOS DE EQUIPOS EDUCATIVOS COMO ACTIVO FIJO PARA ESTADOS FINANCIEROS", title_style)
    elements.append(title)

    fecha_str = datetime.now().strftime('%d/%m/%Y %H:%M')
    info_empresa = Paragraph("Gestion de Activos Fijos", styles['Normal'])
    info_fecha = Paragraph(f"Fecha de generación: {fecha_str}", styles['Normal'])
    elements.extend([info_empresa, info_fecha, Spacer(1, 12)])

    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.white,
        alignment=1,
        backColor=colors.HexColor('#3498db')
    )
    headers = [
        Paragraph("<b>Descripción</b>", header_style),
        Paragraph("<b>Categoria</b>", header_style),
        Paragraph("<b>Modelo</b>", header_style),
        Paragraph("<b>Estado</b>", header_style),
        Paragraph("<b>Fecha de Incorporación</b>", header_style),
        Paragraph("<b>Costo Inicial</b>", header_style),
        Paragraph("<b>Fac. Actualización</b>", header_style),
        Paragraph("<b>Costo Actualizado</b>", header_style),
        Paragraph("<b>Depreciación Acumulada</b>", header_style),
        Paragraph("<b>Valor Neto</b>", header_style)  
    ]
    def formatear_variable(valor):
        return f"{valor:.5f}".rstrip('0').rstrip('.')

    data = [headers]
    for v in recreativos:
        data.append([
            v.descripcion,
            v.categoria,
            v.modelo,
            v.estado,
            v.fecha_incorporacion.strftime('%d/%m/%Y'),
            f"Bs{formatear_variable(v.costo_inicial)}",
            f"{v.factor_de_actualizacion:,.7g}",
            f"Bs{formatear_variable(v.costo_actualizado)}",
            f"Bs{formatear_variable(v.depreciacion_acumulada)}",
            f"Bs{formatear_variable(v.valor_neto)}"
        ])

    table = Table(data, colWidths=[
           1.0*inch,  # Descripción
            0.9*inch,  # categoria
            0.8*inch,  # Modelo
            0.8*inch,  # Estado
            1.1*inch,  # Fecha
            1.2*inch,  # Costo Inicial
            1.0*inch,  # Factor de Actualización
            1.1*inch,  # Costo Actualizado
            1.2*inch,  # Depreciación Acumulada
            1.2*inch  
    ])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f9f9f9'), colors.white])
    ]))

    elements.append(table)

    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#7f8c8d'))
        canvas.drawString(inch, 0.5*inch, f"Total de Equipos Educativos: {len(recreativos)}")
        canvas.drawRightString(landscape(letter)[0] - inch, 0.5*inch, f"Página {doc.page}")
        canvas.setStrokeColor(colors.black)
        canvas.line(inch, inch, 3*inch, inch)
        canvas.drawString(inch, 0.75*inch, "Responsable del reporte")
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="financiero.pdf",
        mimetype='application/pdf'
    )

@recreativo_bp.route('/asignacion', methods=['GET'])
def asignacion():
    recreativos = Recreativo.get_all()
    return equipo_recreativo_view.asignacion(recreativos)












@recreativo_bp.route('/recreativos/imprimir_asignacion', methods=['POST'])
def imprimir_asignacion():
    funcionario = request.form['funcionario']
    cargo = request.form['cargo']
    codigo_barras = request.form['codigo_barras']
     #cambios echos
    recreativo_id = request.form.get('recreativo_id')
    
    if not recreativo_id:
        return "Error: No se recibió el ID del vehículo.", 400
    
    #cambios echos
    recreativo = Recreativo.get_by_id(int(recreativo_id))
    if not recreativo:
        return "Error: Vehículo no encontrado.", 404
    
  
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )

    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=1,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20
    )
    title = Paragraph("ACTA DE ASIGNACIÓN DE ACTIVO FIJO EQUIPOS EDUCATIVOS", title_style)
    elements.append(title)

    fecha_str = datetime.now().strftime('%d/%m/%Y %H:%M')
    info_empresa = Paragraph("Gestion de Activos Fijos", styles['Normal'])
    info_fecha = Paragraph(f"Fecha de generación: {fecha_str}", styles['Normal'])
    elements.extend([info_empresa, info_fecha, Spacer(1, 12)])

    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.white,
        alignment=1,
        backColor=colors.HexColor('#3498db')
    )
    headers = [
        Paragraph("<b>Descripción</b>", header_style),
        Paragraph("<b>Categoria</b>", header_style),
        Paragraph("<b>Modelo</b>", header_style),
        Paragraph("<b>Estado</b>", header_style),
        Paragraph("<b>Fecha de Incorporación</b>", header_style),
        Paragraph("<b>Nombre del Funcionario</b>", header_style),
        Paragraph("<b>Cargo</b>", header_style),
        Paragraph("<b>Nombre Jefe Activos</b>", header_style),
        Paragraph("<b>Cargo</b>", header_style),
        Paragraph("<b>Código de Barras</b>", header_style)  
    ]
  
    
    
    normal_style = ParagraphStyle(
        'NormalWrap',
        parent=styles['Normal'],
        fontSize=9,
        leading=10
    )
    data = [headers]
    
    data.append([
            Paragraph(recreativo.descripcion, normal_style),
            Paragraph(recreativo.categoria, normal_style),
            Paragraph(recreativo.modelo, normal_style),
            Paragraph(recreativo.estado, normal_style),
            Paragraph(recreativo.fecha_incorporacion.strftime("%d/%m/%Y") if recreativo.fecha_incorporacion else "", normal_style),
            Paragraph(funcionario, normal_style),
            Paragraph(cargo, normal_style),
            Paragraph(recreativo.responsable if recreativo.responsable else "—", normal_style),
            Paragraph(recreativo.cargo if recreativo.cargo else "—", normal_style),
            Paragraph(codigo_barras, normal_style)
    ])

    table = Table(data, colWidths=[
           1.0*inch,  # Descripción
            0.9*inch,  # categoria
            0.8*inch,  # Modelo
            0.8*inch,  # Estado
            1.1*inch,  # Fecha
            1.2*inch,  # Costo Inicial
            1.0*inch,  # Factor de Actualización
            1.1*inch,  # Costo Actualizado
            1.2*inch,  # Depreciación Acumulada
            1.2*inch  
    ])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f9f9f9'), colors.white])
    ]))

    elements.append(table)

    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#7f8c8d'))
        canvas.drawString(inch, 0.5*inch, f"Total de Equipos Educativos:1")
        canvas.drawRightString(landscape(letter)[0] - inch, 0.5*inch, f"Página {doc.page}")
        canvas.setStrokeColor(colors.black)
        canvas.line(inch, inch, 3*inch, inch)
        canvas.drawString(inch, 0.75*inch, "Firma del Autor")
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="Acta de Asignacion.pdf",
        mimetype='application/pdf'
    )
    
    
    
    
    
    
    
    
    
    
    
    
@recreativo_bp.route('/recreativos/imprimir_reasignacion', methods=['POST'])
def imprimir_reasignacion():
    jefe_activo = request.form['jefe_activos']
    cargo_jefe = request.form['cargo_jefe']
    funcionario = request.form['funcionario']
    cargo = request.form['cargo']
    codigo_barras = request.form['codigo_barras']
     #cambios echos
    recreativo_id = request.form.get('recreativo_id')
    if not recreativo_id:
        return "Error: No se recibió el ID del vehículo.", 400
    
    #cambios echos
    recreativo = Recreativo.get_by_id(int(recreativo_id))
    if not recreativo:
        return "Error: Vehículo no encontrado.", 404
    
   
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )

    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=1,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20
    )
    title = Paragraph("ACTA DE REASIGNACIÓN DE ACTIVO FIJO EQUIPOS EDUCATIVOS", title_style)
    elements.append(title)

    fecha_str = datetime.now().strftime('%d/%m/%Y %H:%M')
    info_empresa = Paragraph("Gestion de Activos Fijos", styles['Normal'])
    info_fecha = Paragraph(f"Fecha de generación: {fecha_str}", styles['Normal'])
    elements.extend([info_empresa, info_fecha, Spacer(1, 12)])

    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.white,
        alignment=1,
        backColor=colors.HexColor('#3498db')
    )
    headers = [
        Paragraph("<b>Descripción</b>", header_style),
        Paragraph("<b>Categoria</b>", header_style),
        Paragraph("<b>Modelo</b>", header_style),
        Paragraph("<b>Estado</b>", header_style),
        Paragraph("<b>Fecha de Incorporación</b>", header_style),
        Paragraph("<b>Nombre del Funcionario</b>", header_style),
        Paragraph("<b>Cargo</b>", header_style),
        Paragraph("<b>Nombre Jefe Activos</b>", header_style),
        Paragraph("<b>Cargo</b>", header_style),
        Paragraph("<b>Código de Barras</b>", header_style)  
    ]
  
    
    
    normal_style = ParagraphStyle(
        'NormalWrap',
        parent=styles['Normal'],
        fontSize=9,
        leading=10
    )
    data = [headers]
    for v in recreativos:
        data.append([
            Paragraph(recreativo.descripcion, normal_style),
            Paragraph(recreativo.categoria, normal_style),
            Paragraph(recreativo.modelo, normal_style),
            Paragraph(recreativo.estado, normal_style),
            Paragraph(recreativo.fecha_incorporacion.strftime("%d/%m/%Y") if recreativo.fecha_incorporacion else "", normal_style),
            Paragraph(funcionario, normal_style),
            Paragraph(cargo, normal_style),
            Paragraph(jefe_activo,normal_style),
            Paragraph(cargo_jefe,normal_style),
            Paragraph(codigo_barras, normal_style)
        ])

    table = Table(data, colWidths=[
           1.0*inch,  # Descripción
            0.9*inch,  # categoria
            0.8*inch,  # Modelo
            0.8*inch,  # Estado
            1.1*inch,  # Fecha
            1.2*inch,  # Costo Inicial
            1.0*inch,  # Factor de Actualización
            1.1*inch,  # Costo Actualizado
            1.2*inch,  # Depreciación Acumulada
            1.2*inch  
    ])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f9f9f9'), colors.white])
    ]))

    elements.append(table)

    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#7f8c8d'))
        canvas.drawString(inch, 0.5*inch, f"Total Equipos Educativos:1")
        canvas.drawRightString(landscape(letter)[0] - inch, 0.5*inch, f"Página {doc.page}")
        canvas.setStrokeColor(colors.black)
        canvas.line(inch, inch, 3*inch, inch)
        canvas.drawString(inch, 0.75*inch, "Firma del Autor")
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="Acta de Reasignacion.pdf",
        mimetype='application/pdf'
    )    
    
        
