from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import textwrap

def gerar_certificado_pdf(nome_usuario, nome_curso, numero_horas, caminho_certificado='back\website\static\certificado.pdf'):

    largura, altura = letter  
    c = canvas.Canvas(caminho_certificado, pagesize=letter)
    # Desenha o retângulo bege atrás
    c.setFillColorRGB(255/255, 227/255,172/255)
    c.rect(largura/2-280, altura-766, 560, 740,fill=1, stroke=0)
    #Dá pra colocar a logo tbm quando a gente tiver um rs
    
    c.setFont("Helvetica-Bold", 24)
    c.setFillColorRGB(0,0,0)
    c.drawCentredString(largura / 2, altura - 100, "Certificado de Conclusão")
    
    c.setFont("Helvetica", 14)
    texto = (f"Certificamos que {nome_usuario} concluiu com sucesso o curso\n"
             f"'{nome_curso}' com carga horária de {numero_horas} horas.")
    

    linhas = textwrap.wrap(texto, width=60)  

    y_posicao = altura - 200  
    for linha in linhas:
        c.drawCentredString(largura / 2, y_posicao, linha)
        y_posicao -= 20 

    # Assinatura do coordenador
    c.setFont("Helvetica", 12)
    c.drawCentredString(largura / 2, 200, "_______________________")
    c.drawCentredString(largura / 2, 180, "Responsável pelo Curso")
    
    c.save()
    print(f"Certificado salvo em: {caminho_certificado, altura, largura}")
    
    return caminho_certificado


