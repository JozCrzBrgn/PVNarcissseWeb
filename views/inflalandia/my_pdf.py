

from fpdf import FPDF
import os
from datetime import datetime as dt

DIRECCION = "Mi direccion"

class PDF(FPDF):
    def __init__(self, nombre, imagen_pdf, dir_pdf):
        super().__init__()
        self.nombre = nombre
        self.imagen_pdf = imagen_pdf
        self.dir_pdf = dir_pdf

    def header(self):
        # Colocamos el logo:
        self.image(self.imagen_pdf, x=10, y=10, w=40, h=25)
        # Titulo
        self.set_font("helvetica", "B", 15)
        self.cell(w=50, h=5, txt="", border=0, align='C', fill=0)
        self.multi_cell(w=0, h=5, txt="PASTELERÍAS NARCISSE", border=0, align='C', fill=0)
        self.ln(0.5)
        # Sucursal
        self.set_font("helvetica", "B", 12)
        self.cell(w=50, h=5, txt="", border=0, align='C', fill=0)
        self.multi_cell(w=0, h=5, txt="SUCURSAL: " + self.nombre.upper(), border=0, align='C', fill=0)
        self.ln(0.5)
        # Dirección
        self.set_font('helvetica', '', 9)
        self.cell(w=50, h=5, txt="", border=0, align='C', fill=0)
        self.multi_cell(w=0, h=5, txt=self.dir_pdf, border=0, align='C', fill=0)
        self.ln(0.5)
        # Performing a line break:
        self.ln(10)

    def footer(self):
        # Position cursor at 1.5 cm from bottom:
        self.set_y(-15)
        # Setting font: helvetica italic 8
        self.set_font("helvetica", "I", 8)
        # Printing page number:
        self.cell(0, 10, f"Página {self.page_no()}", align="C")



def CrearPDF(df, nombre_sucursal, image_sucursal, dir_sucursal):
    fecha_hoy = dt.strftime(dt.now(), "%Y-%m-%d")

    #####################
    # CREAMOS UN LIENZO #
    #####################
    pdf = PDF(nombre_sucursal, image_sucursal, dir_sucursal)
    pdf.add_page()
    pdf.set_font("Times", size=12)

    ###################
    # DATOS INICIALES #
    ###################
    pdf.set_font('helvetica', 'B', 12)
    pdf.multi_cell(w=0, h=6, txt="FECHA DE IMPRESIÓN: " + fecha_hoy, border=0, align='R', fill=0)
    pdf.ln(5)

    pdf.set_fill_color(217, 217, 217)
    pdf.set_font('helvetica', 'B', 10)
    altura = 10
    pdf.cell(w=25, h=altura, txt="CLAVE", border=1, align='C', fill=1)
    pdf.cell(w=55, h=altura, txt="DÍA", border=1, align='C', fill=1)
    pdf.cell(w=65, h=altura, txt="CUMPLEAÑEROX", border=1, align='C', fill=1)
    pdf.cell(w=20, h=altura, txt="HORARIO", border=1, align='C', fill=1)
    pdf.multi_cell(w=25, h=altura, txt="CANT. DE PX", border=1, align='C', fill=1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)

    for row in df.values:
      pdf.set_fill_color(255, 255, 255)
      pdf.set_font('helvetica', 'B', 10)
      altura = 10
      pdf.cell(w=25, h=altura, txt=row[0], border=1, align='C', fill=1)
      pdf.cell(w=55, h=altura, txt=row[3], border=1, align='C', fill=1)
      pdf.cell(w=65, h=altura, txt=row[1], border=1, align='C', fill=1)
      pdf.cell(w=20, h=altura, txt=row[4][:-3], border=1, align='C', fill=1)
      pdf.multi_cell(w=25, h=altura, txt=str(row[2]) + " PX", border=1, align='C', fill=1)
      pdf.set_text_color(0, 0, 0)
    
    pdf.add_page()

    #############
    # CLÁUSULAS #
    #############
    pdf.set_fill_color(217, 217, 217)
    pdf.set_font('helvetica', 'B', 10)
    pdf.multi_cell(w=0, h=6, txt="CLÁUSULAS:", border=0, align='L', fill=1)
    pdf.ln(0.1)
    
    clausula_1 = 'Al realizar un pedido se deberá pagar un anticipo correspondiente al 50% del precio total del pastel.'
    clausula_2 = 'Es indispensable que al recoger su pedido de sucursal o entrega de flete presente la orden de compra impresa y/o digital (PDF), sin excepción alguna.'
    clausula_3 = 'Los pasteles de entrega a domicilio deberán liquidarse 72hrs. Antes de la entrega.'
    clausula_4 = 'Una vez firmada esta orden de compra no se podrá realizar ningún tipo de modificación (fecha, flete, diseño o decoración, cubierta y/o número de personas) sin excepción alguna.'
    clausula_5 = 'En pedidos con flete, por cuestiones de tráfico, la hora de entrega puede variar de la hora señalada en la nota (1 horas antes ó 1 horas después).'
    clausula_6 = 'Los pedidos con flete se entregan a pie del lugar asignado, debido a que solo lo lleva el operador, notificar cuando la entrega sea en algún piso en específico.'
    clausula_7 = 'Es indispensable que, al momento de recibir su pedido, solicite al operador el formato de recepción del pedido, el cual deberá llenar y firmar de conformidad.'
    clausula_8 = 'Una vez entregado el producto y firmado de conformidad el formato de entrega, no tendrán efecto las reclamaciones posteriores, principalmente en apariencia visual.'
    clausula_9 = 'En caso de ser la entrega con flete, se le solicita que este en el lugar de entrega una persona para recibirlo ya sea domicilio particular o salón de fiestas.'
    clausula_10 = 'Los pasteles pueden tener alguna variación en cuanto al diseño que se presenta en el catálogo y/o diseño especial (orillas, color, dibujo, etc.) \
        debido a que la decoración es artesanal.'
    clausula_11 = 'Los colores de los Pasteles pueden tener alguna variación en cuanto a la intensidad del color, de igual manera pueden llegar a pintar al momento de ingerirse. \
        Esto no representa algún problema para la salud, porque el colorante es vegetal y 100 % comestible.'
    clausula_12 = 'Para el caso de desear hacer alguna reclamación o queja del producto, es indispensable mandar una imagen con buena resolución y tamaño, evitando imágenes pixeladas.'
    clausula_13 = 'Para cualquier queja es indispensable presentarse en la sucursal con su ticket de compra. Llevar el 80% del producto, en un plazo no mayor a 24hrs.'
    clausula_14 = 'Estimado cliente, hacemos de su conocimiento que, en caso de desear cambiar la cubierta Fondant por cubierta Ganash y/o crema, Pastelería Narcisse \
        no se hace responsable de las diferencias económicas y/o de presentación que el cambio pueda ocasionar (se requiere firma).'

    list_clausulas = [
        clausula_1, clausula_2, clausula_3, clausula_4, clausula_5, clausula_6, clausula_7, clausula_8, clausula_9, clausula_10, clausula_11, clausula_12, clausula_13, clausula_14
        ]
    for i, clausula in enumerate(list_clausulas):
        pdf.set_font('helvetica', 'B', 8)
        pdf.cell(w=10, h=6, txt=str(i+1)+".", border=0, align='R', fill=0)
        pdf.set_font('helvetica', '', 7.5)
        pdf.multi_cell(w=0, h=6, txt=clausula, border=0, align='L', fill=0)
        pdf.ln(0.1)
    pdf.ln(5)


    #################
    # CANCELACIONES #
    #################
    pdf.set_fill_color(217, 217, 217)
    pdf.set_font('helvetica', 'B', 10)
    pdf.multi_cell(w=0, h=6, txt="CANCELACIONES:", border=0, align='L', fill=1)
    pdf.ln(0.1)

    cancelacion_1 = 'La cancelación de pedidos deberá de realizarse personalmente con 3 días antes de su entrega, sin excepción alguna.'
    cancelacion_2 = 'Por concepto de cancelación se retendrá el 50% del total del pedido (anticipo), por gastos generados (base, materia prima, insumos etc).'
    cancelacion_3 = 'No se harán devoluciones en efectivo, solo en especie.'

    for i, cancelacion in enumerate([cancelacion_1, cancelacion_2, cancelacion_3]):
        pdf.set_font('helvetica', 'B', 8)
        pdf.cell(w=10, h=6, txt=str(i+1)+".", border=0, align='R', fill=0)
        pdf.set_font('helvetica', '', 7.5)
        pdf.multi_cell(w=0, h=6, txt=cancelacion, border=0, align='L', fill=0)
        pdf.ln(0.1)

    ##########
    # FIRMAS #
    ##########
    pdf.set_font('helvetica', 'B', 9)
    pdf.ln(20)

    pdf.cell(w=95, h=4, txt="___________________________________", border=0, align='C', fill=0)
    pdf.multi_cell(w=95, h=4, txt="___________________________________", border=0, align='C', fill=0)

    pdf.ln(0.1)
    pdf.cell(w=95, h=6, txt="NOMBRE Y FIRMA DEL REPARTIDOR", border=0, align='C', fill=0)
    pdf.multi_cell(w=95, h=6, txt="NOMBRE Y FIRMA DE QUIEN RECIBE", border=0, align='C', fill=0)

    pdf.ln(0.1)
    pdf.cell(w=95, h=6, txt=fecha_hoy, border=0, align='C', fill=0)
    pdf.multi_cell(w=95, h=6, txt=fecha_hoy, border=0, align='C', fill=0)


    #############
    # CREAR PDF #
    #############
    nombre_archivo = f"./pdf_inflalandia_{dt.strftime(dt.now(), "%Y_%m_%d")}" + ".pdf"
    pdf.output(nombre_archivo)
    return nombre_archivo