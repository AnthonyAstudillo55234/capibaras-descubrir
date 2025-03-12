from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

# Configuración de la base de datos MongoDB Atlas
app.config["MONGO_URI"] = "mongodb+srv://anthony55234:anthony667740@cluster0.0bh5b.mongodb.net/capibaras?retryWrites=true&w=majority"
mongo = PyMongo(app)

@app.route('/')
def index():
    cursos = list(mongo.db.cursos.find())  # Convertir a lista
    return render_template('index.html', cursos=cursos)

@app.route('/crear_curso', methods=['POST'])
def crear_curso():
    nombre_curso = request.form.get('nombre_curso')
    if nombre_curso:
        mongo.db.cursos.insert_one({"nombre": nombre_curso, "estudiantes": []})
    return redirect(url_for('index'))

@app.route('/agregar_estudiante/<curso_id>', methods=['POST'])
def agregar_estudiante(curso_id):
    nombre_estudiante = request.form.get('nombre_estudiante').strip()
    if nombre_estudiante:
        nuevo_estudiante = {"nombre": nombre_estudiante, "capibaras": 0, "comentarios": []}
        mongo.db.cursos.update_one({"_id": ObjectId(curso_id)}, {"$push": {"estudiantes": nuevo_estudiante}})
    return redirect(url_for('index'))

@app.route('/modificar_puntaje/<curso_id>/<estudiante_nombre>', methods=['POST'])
def modificar_puntaje(curso_id, estudiante_nombre):
    accion = request.form.get('accion')
    curso = mongo.db.cursos.find_one({"_id": ObjectId(curso_id)})
    
    if curso:
        estudiantes = curso.get("estudiantes", [])
        for estudiante in estudiantes:
            if estudiante['nombre'] == estudiante_nombre:
                if accion == 'sumar' and estudiante['capibaras'] < 10:
                    estudiante['capibaras'] += 1
                    if estudiante['capibaras'] == 10:
                        mongo.db.cursos.update_one({"_id": ObjectId(curso_id)}, {"$set": {"estudiantes": estudiantes}})
                        return redirect(url_for('premio', estudiante_nombre=estudiante_nombre))
                elif accion == 'restar' and estudiante['capibaras'] > 0:
                    estudiante['capibaras'] -= 1
                mongo.db.cursos.update_one({"_id": ObjectId(curso_id)}, {"$set": {"estudiantes": estudiantes}})
                break
    return redirect(url_for('index'))

@app.route('/eliminar_estudiante/<curso_id>/<estudiante_nombre>', methods=['POST'])
def eliminar_estudiante(curso_id, estudiante_nombre):
    curso = mongo.db.cursos.find_one({"_id": ObjectId(curso_id)})
    
    if curso:
        estudiantes_actualizados = [estudiante for estudiante in curso['estudiantes'] if estudiante['nombre'] != estudiante_nombre]
        mongo.db.cursos.update_one({"_id": ObjectId(curso_id)}, {"$set": {"estudiantes": estudiantes_actualizados}})
    
    return redirect(url_for('index'))

@app.route('/eliminar_curso/<curso_id>', methods=['POST'])
def eliminar_curso(curso_id):
    mongo.db.cursos.delete_one({"_id": ObjectId(curso_id)})
    return redirect(url_for('index'))

@app.route('/premio/<estudiante_nombre>', methods=['GET'])
def premio(estudiante_nombre):
    return render_template('premio.html', estudiante_nombre=estudiante_nombre)

@app.route('/get_cursos', methods=['GET'])
def get_cursos():
    cursos = list(mongo.db.cursos.find({}, {"_id": 1, "nombre": 1, "estudiantes": 1}))
    
    for curso in cursos:
        curso["_id"] = str(curso["_id"])
        for estudiante in curso["estudiantes"]:
            estudiante["capibaras"] = int(estudiante["capibaras"])

    return jsonify(cursos)

@app.route('/carrera')
def carrera():
    return render_template('carrera.html')

@app.route('/agregar_comentario/<curso_id>/<estudiante_nombre>', methods=['POST'])
def agregar_comentario(curso_id, estudiante_nombre):
    comentario = request.form.get('comentario')
    curso = mongo.db.cursos.find_one({"_id": ObjectId(curso_id)})
    
    if curso:
        estudiantes = curso.get("estudiantes", [])
        for estudiante in estudiantes:
            if estudiante["nombre"] == estudiante_nombre:
                if "comentarios" not in estudiante:
                    estudiante["comentarios"] = []  # Se asegura de que la clave exista
                estudiante["comentarios"].append(comentario)

                mongo.db.cursos.update_one(
                    {"_id": ObjectId(curso_id)},
                    {"$set": {"estudiantes": estudiantes}}
                )
                break

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)