from flask import Flask, render_template, request,flash,redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,DateField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
# #Add Database 
# ##app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# ##app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:''@localhost/cliente"

# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqldb://root@127.0.0.1/client"

#                                         # "mysql+mysqldb://scott:tiger@192.168.0.134/test"

#Add Database 
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqldb://root@127.0.0.1:3308/examen"

app.config['SECRET_KEY']='My super secret that no one is supposed to know'
#Initialize the Database
db =SQLAlchemy(app)

#Create Model ESTUDIANTE
class Estudiante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(40), nullable=False)
    apellido = db.Column(db.String(40), nullable=False)
    DNI = db.Column(db.Integer, unique=True)
    fechaNacimiento = db.Column(db.DateTime)
    sexo = db.Column(db.String(10))
    matricula = db.relationship('Matricula', backref='estudiante', lazy=True)

#Create Model ESCUELA
class Escuela(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(60), unique=True)
    nombre = db.Column(db.String(64), nullable=False)
    duracion = db.Column(db.Integer)
    matricula = db.relationship('Matricula', backref='escuela', lazy=True)
    
#Create Model CURSO
class Curso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    credito = db.Column(db.String(120), nullable=False)
    matricula = db.relationship('Matricula', backref='curso', lazy=True)

#Create Model MATRICULA
class Matricula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    escuela_id=db.Column(db.Integer,db.ForeignKey('escuela.id'),nullable=False)
    estudiante_id=db.Column(db.Integer,db.ForeignKey('estudiante.id'),nullable=False)
    curso_id=db.Column(db.Integer,db.ForeignKey('curso.id'),nullable=False)
 
#FORMULARIOS
class EscuelaForm(FlaskForm):
    codigoEscuela =StringField('codigo', validators=[DataRequired()])
    nombreEscuela=StringField('nombre', validators=[DataRequired()])
    duracionEscuela =StringField('duracion', validators=[DataRequired()])

class EstudianteForm(FlaskForm):
    nombres =StringField('nombres', validators=[DataRequired()])
    apellido=StringField('apellido', validators=[DataRequired()])
    DNI =StringField('DNI', validators=[DataRequired()])
    fechaNacimiento=DateField('fechaNacimiento', validators=[DataRequired()])
    sexo=StringField('sexo', validators=[DataRequired()])

class CursoForm(FlaskForm):
    codigoCurso =StringField('codigo', validators=[DataRequired()])
    nombreCurso=StringField('nombre', validators=[DataRequired()])
    creditoCurso =StringField('credito', validators=[DataRequired()])

@app.route('/',methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/insertar',methods=['GET','POST'])
def insertar():
    form_student = EstudianteForm()
    form_Escuela = EscuelaForm()
    form_Curso = CursoForm()
    curso = None
    estudiante = None
    escuela = None

    if form_student.validate_on_submit():
        estudiante = Estudiante.query.filter_by(DNI = form_student.DNI.data).first()
        if estudiante is None:
            estudiante = Estudiante(nombres = form_student.nombres.data, apellido = form_student.apellido.data,
            DNI = form_student.DNI.data,fechaNacimiento = form_student.fechaNacimiento.data, sexo = form_student.sexo.data,)
            db.session.add(estudiante)
            db.session.commit()
  
    else: return render_template('insertar.html',form_student=form_student,form_Escuela=form_Escuela,form_Curso=form_Curso)
    
    if form_Escuela.validate_on_submit():
        escuela = Escuela.query.filter_by(codigo = form_Escuela.codigoEscuela.data).first()
        if escuela is None:
            escuela = Escuela(codigo = form_Escuela.codigoEscuela.data, nombre = form_Escuela.nombreEscuela.data, duracion = form_Escuela.duracionEscuela.data)
            db.session.add(escuela)
            db.session.commit()
        flash("Usuario añadido con exito")
    else: return render_template('insertar.html',form_student=form_student,form_Escuela=form_Escuela,form_Curso=form_Curso)
    
    
    if form_Curso.validate_on_submit():
        curso = Curso.query.filter_by(codigo = form_Curso.codigoCurso.data).first()
        if curso is None:
            curso = Curso(codigo= form_Curso.codigoCurso.data, nombre = form_Curso.nombreCurso.data, credito = form_Curso.creditoCurso.data)
            db.session.add(curso)
            db.session.commit()
       
    else: return render_template('insertar.html',form_student=form_student,form_Escuela=form_Escuela,form_Curso=form_Curso)

    estudiante_id=Estudiante.query.filter_by(DNI=estudiante.DNI).first().id
    curso_id=Curso.query.filter_by(codigo=curso.codigo).first().id
    escuela_id=Escuela.query.filter_by(codigo=escuela.codigo).first().id

    db.session.add(Matricula(estudiante_id=estudiante_id, curso_id=curso_id, escuela_id=escuela_id))
    db.session.commit()
    return redirect(url_for('matricula'))

@app.route('/estudiante')
def estudiante():
    estudiantes=Estudiante.query.order_by(Estudiante.id)
    return render_template('estudiante.html',estudiantes=estudiantes)

@app.route('/escuela')
def escuela():
    escuelas=Escuela.query.order_by(Escuela.id)
    return render_template('escuela.html',escuelas=escuelas)

@app.route('/curso',methods=['GET'])
def curso():
    cursos = Curso.query.order_by(Curso.id)
    return render_template('curso.html',cursos=cursos)

@app.route('/matricula')
def matricula():
    matriculaS=Matricula.query.order_by(Matricula.id)
    lista=[]
    for matricula in matriculaS:
        estudiante = Estudiante.query.filter_by(id=matricula.estudiante_id).first()
        escuela = Escuela.query.filter_by(id=matricula.escuela_id).first()
        curso = Curso.query.filter_by(id=matricula.curso_id).first()
        lista.append({
            "nombreEscuela":escuela.nombre,
            "nombreCurso":curso.nombre,
            "nombreEstudiante":estudiante.nombres
        })    
    return render_template('matricula.html',lista=lista)









