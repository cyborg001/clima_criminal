import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import inch

def generar_boletin_pdf(datos_reportes, estadisticas, filtro_sector="Todos"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f172a'),
        alignment=0
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#dc2626'),
        textTransform='uppercase'
    )
    
    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#64748b')
    )

    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#1e293b')
    )

    cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#0f172a')
    )

    header_cell = ParagraphStyle(
        'HeaderCell',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.white
    )

    # 1. Encabezado Institucional
    story.append(Paragraph("CLIMA CRIMINAL &bull; INTELIGENCIA GEOESPACIAL URBANA", subtitle_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Boletín Ejecutivo de Seguridad Ciudadana", title_style))
    
    fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M")
    sector_txt = filtro_sector if filtro_sector != "Todos" else "Gran Santo Domingo (Prioridad: Santo Domingo Este)"
    story.append(Paragraph(f"<b>Área analizada:</b> {sector_txt} &nbsp;|&nbsp; <b>Fecha de emisión:</b> {fecha_hoy} &nbsp;|&nbsp; <b>Fuente:</b> Red Comunitaria Anónima", meta_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0f172a'), spaceBefore=2, spaceAfter=12))

    # 2. Resumen Ejecutivo (Cards de Métricas en Tabla)
    total_inc = estadisticas.get("total_reportes", len(datos_reportes))
    top_sector = estadisticas.get("top_sectores_sde", [{}])[0].get("sector", "N/A") if estadisticas.get("top_sectores_sde") else "N/A"
    delito_frec = estadisticas.get("delito_frecuente", "N/A")
    horario_crit = estadisticas.get("horario_critico", "N/A")

    kpi_data = [
        [
            Paragraph("TOTAL DE INCIDENTES", meta_style),
            Paragraph("SECTOR MÁS CALIENTE (SDE)", meta_style),
            Paragraph("DELITO PREDOMINANTE", meta_style),
            Paragraph("HORARIO CRÍTICO", meta_style)
        ],
        [
            Paragraph(f"<font size=14 color='#0f172a'><b>{total_inc}</b></font>", cell_style),
            Paragraph(f"<font size=11 color='#dc2626'><b>{top_sector}</b></font>", cell_style),
            Paragraph(f"<font size=11 color='#f97316'><b>{delito_frec}</b></font>", cell_style),
            Paragraph(f"<font size=11 color='#7c3aed'><b>{horario_crit}</b></font>", cell_style)
        ]
    ]
    t_kpi = Table(kpi_data, colWidths=[1.85*inch, 1.85*inch, 1.85*inch, 1.85*inch])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 14))

    # 3. Tabla de Incidentes Recientes Detallados
    story.append(Paragraph("<b>Registro Detallado de Incidentes y Reportes Recientes</b>", ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor('#0f172a'))))
    story.append(Spacer(1, 6))

    table_data = [
        [
            Paragraph("Fecha", header_cell),
            Paragraph("Sector", header_cell),
            Paragraph("Tipo de Delito", header_cell),
            Paragraph("Horario", header_cell),
            Paragraph("Referencia / Descripción", header_cell),
            Paragraph("Precisión", header_cell)
        ]
    ]

    for rep in datos_reportes[:35]:  # primeros 35
        fecha_str = rep.get("fecha_reporte", "").split(" ")[0] if rep.get("fecha_reporte") else "Reciente"
        sector_nombre = rep.get("sector", "N/A")
        delito_nom = rep.get("tipo_delito", "")
        if rep.get("tipo_personalizado"):
            delito_nom += f" ({rep.get('tipo_personalizado')})"
            
        franja = rep.get("franja_horaria", "N/A")
        
        desc = rep.get("referencia_publica", "")
        if rep.get("descripcion"):
            if desc:
                desc += f" - {rep.get('descripcion')}"
            else:
                desc = rep.get("descripcion")
        if not desc:
            desc = "Sin detalle adicional"
        if len(desc) > 55:
            desc = desc[:52] + "..."
            
        precision = "Exacta" if rep.get("modo_ubicacion") == "exacta" else "Protegida"
        prec_color = "#0284c7" if precision == "Exacta" else "#7c3aed"

        table_data.append([
            Paragraph(fecha_str, cell_style),
            Paragraph(f"<b>{sector_nombre}</b>", cell_style),
            Paragraph(delito_nom, cell_bold),
            Paragraph(franja, cell_style),
            Paragraph(desc, cell_style),
            Paragraph(f"<font color='{prec_color}'>{precision}</font>", cell_style)
        ])

    t_reportes = Table(table_data, colWidths=[0.85*inch, 1.4*inch, 1.5*inch, 0.75*inch, 2.1*inch, 0.8*inch])
    t_reportes.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#f1f5f9')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_reportes)

    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94a3b8'), spaceBefore=2, spaceAfter=6))
    story.append(Paragraph(
        "<b>Aviso de Confidencialidad y Seguridad:</b> Este documento consolida reportes comunitarios anónimos con fines preventivos y de alerta temprana. "
        "Los reportes en modo protegido han sido desfasados deliberadamente para salvaguardar la identidad y seguridad de las víctimas. "
        "Generado automáticamente por el motor de Clima Criminal &bull; ramirezsoft.com",
        ParagraphStyle('FooterNote', fontName='Helvetica-Oblique', fontSize=7, leading=9, textColor=colors.HexColor('#94a3b8'))
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
