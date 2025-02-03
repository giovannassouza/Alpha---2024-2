from flask import Blueprint, jsonify, request, render_template
from flask_wtf.csrf import generate_csrf, CSRFProtect
from .models import *
from website.models import *
from datetime import datetime
from .api_key import *

#gerar perguntas
from langchain_community.chat_models import ChatMaritalk
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts.chat import ChatPromptTemplate
import os
from dotenv import load_dotenv
from random import shuffle
from abc import ABC, abstractmethod


class llm_model(ABC):
    @abstractmethod
    def __init__(self):
        pass

    def gerar_perguntas(self):
        pass

class sabia_3(llm_model):

    def __init__(self):
        """
        Inicializa o modelo sabia-3 e verifica se a chave de API foi configurada corretamente.
        """
        api_key = maritaca_api
        if not api_key:
            #error
            return None
        
        self.llm = ChatMaritalk(
            model="sabia-3",
            api_key=api_key,
            temperature=0.7,
            max_tokens=8000,
        )

    def gerar_perguntas(self, transcricao, num_perguntas):
        chat_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """Crie exatamente {num_perguntas} perguntas com 4 alternativas cada, a partir de uma transcrição de aula fornecida,
                no formato CSV, onde cada linha contém a pergunta, as 4 alternativas, e a resposta correta, separadas por ;.
                A primeira coluna será a pergunta, a segunda coluna terá a alternativa 1, a terceira coluna terá a alternativa 2,
                a quarta coluna terá a alternativa 3, a quinta coluna terá a alternativa 4 e a sexta coluna terá a resposta correta.
                As perguntas devem ser claras, objetivas e concisas, e todas as alternativas devem ser apresentadas de forma coerente.
                Não adicione texto antes ou depois das perguntas e alternativas e nenhuma outra formatação no arquivo CSV. A reposta deve
                ser o texto da alternativa correta. Não apenas as perguntas e respostas nas linhas, sem a indicação do número da pergunta."""), 
                ("human", f"A transcrição é: {transcricao}"),
            ]
        )

        output_parser = StrOutputParser()
        chain = chat_prompt | self.llm | output_parser

        result = chain.invoke({"transcricao": transcricao , "num_perguntas": num_perguntas})
        
        return self.formatar(result)
    
    def formatar(self, string):
        perguntas = []
        for linha in string[7:-4].split("\n"):
            partes = linha.split(";")
            pergunta_texto = partes[0]
            alternativas = partes[1:-1]
            resposta_correta = partes[-1]
            shuffle(alternativas)
            perguntas.append(Pergunta(pergunta_texto, alternativas, resposta_correta))
        return perguntas
    
class Pergunta:
    def __init__(self, pergunta, alternativas, resposta_correta):
        self.pergunta = pergunta
        self.alternativas = alternativas
        self.resposta_correta = resposta_correta

    def to_dict(self):
        """Converte o objeto Pergunta para um dicionário JSON-friendly."""
        return {
            "pergunta": self.pergunta,
            "alternativas": {
                "A": self.alternativas[0],
                "B": self.alternativas[1],
                "C": self.alternativas[2],
                "D": self.alternativas[3],
            },
            "resposta_correta": self.resposta_correta
        }

    def __str__(self):
        return f"{self.pergunta}\nAlternativas: {'; '.join(self.alternativas)}\nResposta correta: {self.resposta_correta}"


quiz = Blueprint('quiz',__name__)

@quiz.route('/quiz/forms', methods = ['GET','POST'])
def quizWrite():
    if(request.method == 'POST'):
        enunciado = request.form.get('enunciado')
        alternativa_A = request.form.get('alternativa_A')
        alternativa_B = request.form.get('alternativa_B')
        alternativa_C = request.form.get('alternativa_C')
        alternativa_D = request.form.get('alternativa_D')
        alternativa_E = request.form.get('alternativa_E')
        resposta_correta = request.form.get('resposta_correta')
        question = Questao(enunciado = enunciado, alternativa_A = alternativa_A, alternativa_B = alternativa_B, alternativa_C = alternativa_C, alternativa_D = alternativa_D, alternativa_E = alternativa_E, resposta_correta=resposta_correta)
        db.session.add(question)
        db.session.commit()
    return render_template('new_question_form.html')

@quiz.route('/quiz', methods = ['GET'])
def quizRead():
    try:
        questionario = db.session.execute(db.select(Questionario).filter_by(id = 1)).scalar_one()

        questionIdFromQuestionario = [questionario.q1, questionario.q2, questionario.q3, questionario.q4, questionario.q5]
        qText = ""
        for question in questionIdFromQuestionario:
            qX = db.session.execute(db.select(Questao).filter_by(id = question)).scalar_one()
            qText += qX.enunciado + '<ul>'
            qText += '<li>' + qX.alternativa_A + '</li>'
            qText += '<li>' + qX.alternativa_B + '</li>'
            qText += '<li>' + qX.alternativa_C + '</li>'
            qText += '<li>' + qX.alternativa_D + '</li>'
            qText += '<li>' + qX.alternativa_E + '</li>'
            qText += '<li>' + qX.resposta_correta + '</li>'
            qText += '</ul>'
        return qText
    
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text


@quiz.route('/quiz/generate', methods=['POST'])
def gerar_perguntas():
    try:
        # Obtém os dados JSON da requisição
        data = request.get_json()

        # Valida se os campos obrigatórios estão presentes
        if 'transcricao' not in data or 'num_perguntas' not in data:
            return jsonify({"erro": "Campos 'transcricao' e 'num_perguntas' são obrigatórios!"}), 400

        transcricao = data['transcricao']
        num_perguntas = data['num_perguntas']

        # Certifica-se de que num_perguntas é um número válido
        if not isinstance(num_perguntas, int) or num_perguntas <= 0:
            return jsonify({"erro": "O campo 'num_perguntas' deve ser um número inteiro positivo!"}), 400

        # Inicializa o modelo e gera perguntas
        modelo = sabia_3()
        perguntas = modelo.gerar_perguntas(transcricao, num_perguntas)

        # Converte a saída para JSON
        perguntas_json = [p.to_dict() for p in perguntas]

        return jsonify({"perguntas": perguntas_json})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
