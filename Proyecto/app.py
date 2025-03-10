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
    nombre_estudiante = request.form.get('nombre_estudiante')
    if nombre_estudiante:
        mongo.db.cursos.update_one({"_id": ObjectId(curso_id)}, {"$push": {"estudiantes": {"nombre": nombre_estudiante, "capibaras": 0}}})
    return redirect(url_for('index'))

@app.route('/modificar_puntaje/<curso_id>/<estudiante_nombre>', methods=['POST'])
def modificar_puntaje(curso_id, estudiante_nombre):
    accion = request.form.get('accion')
    curso = mongo.db.cursos.find_one({"_id": ObjectId(curso_id)})
    
    for estudiante in curso['estudiantes']:
        if estudiante['nombre'] == estudiante_nombre:
            if accion == 'sumar':
                estudiante['capibaras'] += 1
            elif accion == 'restar' and estudiante['capibaras'] > 0:
                estudiante['capibaras'] -= 1
            if estudiante['capibaras'] >= 10:
                # Redirige a la página de premio si el estudiante llega a 10 capibaras
                return redirect(url_for('premio', estudiante_nombre=estudiante_nombre))
            mongo.db.cursos.update_one({"_id": ObjectId(curso_id)}, {"$set": {"estudiantes": curso['estudiantes']}})
            break
    return redirect(url_for('index'))


@app.route('/eliminar_estudiante/<curso_id>/<estudiante_nombre>', methods=['POST'])
def eliminar_estudiante(curso_id, estudiante_nombre):
    # Buscar el curso
    curso = mongo.db.cursos.find_one({"_id": ObjectId(curso_id)})
    
    # Filtrar los estudiantes para eliminar al estudiante
    estudiantes_actualizados = [estudiante for estudiante in curso['estudiantes'] if estudiante['nombre'] != estudiante_nombre]
    
    # Actualizar el curso sin el estudiante eliminado
    mongo.db.cursos.update_one({"_id": ObjectId(curso_id)}, {"$set": {"estudiantes": estudiantes_actualizados}})
    
    return redirect(url_for('index'))

@app.route('/eliminar_curso/<curso_id>', methods=['POST'])
def eliminar_curso(curso_id):
    # Eliminar el curso de la base de datos
    mongo.db.cursos.delete_one({"_id": ObjectId(curso_id)})
    
    return redirect(url_for('index'))

@app.route('/premio/<estudiante_nombre>', methods=['GET'])
def premio(estudiante_nombre):
    return render_template('premio.html', estudiante_nombre=estudiante_nombre)

if __name__ == '__main__':
    app.run(debug=True)