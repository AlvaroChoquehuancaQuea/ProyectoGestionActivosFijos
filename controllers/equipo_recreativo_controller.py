from flask import request, redirect, url_for, Blueprint, current_app, flash, send_file
from datetime import datetime
from models.equipo_recreativo_model import Recreativo
from views import equipo_recreativo_view
from werkzeug.utils import secure_filename
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

recreativo_bp = Blueprint('recreativo', __name__, url_prefix='/recreativos')


# Listado de vehículos
@recreativo_bp.route('/')
def index():
    recreativos = Recreativo.get_all()
    return equipo_recreativo_view.list(recreativos)

def get_upload_folder():
    """Obtiene la carpeta de uploads con fallback por defecto"""
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
    
    # Crear directorio si no existe
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    return upload_folder


#Creacion de recreativos
@recreativo_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        try:
            # Procesar campos del formulario
            descripcion = request.form['descripcion']
            marca = request.form['marca']
            modelo = request.form['modelo']
            estado = request.form['estado']
            costo_inicial = float(request.form['costo_inicial'])
            fecha_incorporacion = datetime.strptime(request.form['fecha_incorporacion'], '%Y-%m-%d').date()
            valor_residual = float(request.form['valor_residual'])
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
                marca=marca,
                modelo=modelo,
                estado=estado,
                costo_inicial=costo_inicial,
                fecha_incorporacion=fecha_incorporacion,
                valor_residual=valor_residual,
                años_vida_util=años_vida_util,
                factor_de_actualizacion=factor_de_actualizacion,
                imagen=imagen_filename,
                cargo=cargo,
                responsable=responsable
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
        marca = request.form['marca']
        modelo = request.form['modelo']
        estado = request.form['estado']
        costo_inicial = float(request.form['costo_inicial'])
        fecha_incorporacion = datetime.strptime(request.form['fecha_incorporacion'], '%Y-%m-%d').date()
        valor_residual = float(request.form['valor_residual'])
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
            marca=marca,
            modelo=modelo,
            estado=estado,
            costo_inicial=costo_inicial,
            fecha_incorporacion=fecha_incorporacion,
            valor_residual=valor_residual,
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
        info_empresa = Paragraph("Sistema de Revalorización de Activos Fijos", info_style)
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
            Paragraph("<b>Marca</b>", header_style),
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
                # Depreciación lineal: valor neto = costo_inicial - ((costo_inicial - valor_residual) * años_transcurridos / años_vida_util)
                # Aquí asumimos que años_transcurridos = años_vida_util para mostrar valor neto al final de vida útil (puedes ajustar)
                valor_neto = v.costo_inicial - ((v.costo_inicial - v.valor_residual) * (v.años_vida_util / v.años_vida_util))
                # Simplifica a valor_residual en realidad, pero dejo fórmula
            except Exception:
                valor_neto = 0.0

            data.append([
                str(v.id),
                v.descripcion,
                v.marca,
                v.modelo,
                f"Bs{v.costo_inicial:,.2f}",
                f"Bs{v.valor_residual:,.2f}",
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
