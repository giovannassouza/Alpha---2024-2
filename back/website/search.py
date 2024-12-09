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
