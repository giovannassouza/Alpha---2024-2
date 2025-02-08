from flask import Flask, request, jsonify
from models import db, Curso  
from api_key import DB_NAME
app = Flask(__name__)

# Configuração do banco de dados
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o banco
db.init_app(app)

# Rota de pesquisa
@app.route('/search', methods=['GET'])
def search():
    """
    Endpoint to search for courses.
    ---
    tags:
      - Search
    parameters:
      - name: q
        in: query
        type: string
        required: false
        description: Search query.
    responses:
      200:
        description: Search results.
        schema:
          type: object
          properties:
            query:
              type: string
              description: The search query.
            results:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    description: Course ID.
                  nome:
                    type: string
                    description: Course name.
                  descricao:
                    type: string
                    description: Course description.
                  horas_estimado:
                    type: integer
                    description: Estimated hours.
                  texto_certificado:
                    type: string
                    description: Certificate text.
                  questionario_id:
                    type: integer
                    description: Questionnaire ID.
    """
    query = request.args.get('q', '')

    results = Curso.query.filter(
        (Curso.nome.ilike(f"%{query}%")) |
        (Curso.descricao.ilike(f"%{query}%"))
    ).all()

    results_json = [
        {
            "id": curso.id,
            "nome": curso.nome,
            "descricao": curso.descricao,
            "horas_estimado": curso.horas_estimado,
            "texto_certificado": curso.texto_certificado,
            "questionario_id": curso.questionario_id
        }
        for curso in results
    ]

    return jsonify({"query": query, "results": results_json})

if __name__ == '__main__':
    app.run(debug=True)
