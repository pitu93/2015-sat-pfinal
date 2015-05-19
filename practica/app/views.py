# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
import urllib2
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import sys
import string
from models import Tabla
from models import Actividad

formu = "<form class = 'uno' action='' method='POST'><h2><span class='entypo-login'></span>Loguéate</h2><button class='submit'><span class='entypo-lock'></span></button><span class='entypo-user inputUserIcon'></span><input type='text' class='user' name='nombre'placeholder='ursername'/><span class='entypo-key inputPassIcon'></span><input type='password' name='contra' class='pass'placeholder='password'/></form>"


def normalize_whitespace(text):
    return string.join(string.split(text), ' ')

def fecha(fecha):
    bien = ''
    bien = fecha.split('-')
    bien[2] = bien[2].split(' ')[0]
    return bien
    
class CounterHandler(ContentHandler):
    
    def __init__ (self):
        self.inContent = 0
        self.theContent = ""
        self.aux = ''
        self.evento = {}
        self.lista = []

    def startElement (self, name, attrs):
        
        if name == 'atributos':
            self.title = normalize_whitespace(attrs.get('idioma'))
            #print " title: " + self.title + "."
        elif name == 'atributo':
            self.aux = normalize_whitespace(attrs.get('nombre')) 
            if(self.aux == 'TITULO' or self.aux == 'TIPO' or self.aux == 'GRATUITO' or self.aux == 'PRECIO' or self.aux == 'FECHA-EVENTO' or              self.aux == 'HORA-EVENTO' or self.aux == 'EVENTO-LARGA-DURACION' or self.aux == 'CONTENT-URL-ACTIVIDAD' or self.aux == 'ID-EVENTO'):
                self.inContent = 1
        
            
    def endElement (self, name):
        if self.inContent:
            self.theContent = normalize_whitespace(self.theContent)
        if name == 'atributo':
            if(self.aux == 'TITULO' or self.aux == 'TIPO' or self.aux == 'GRATUITO' or self.aux == 'PRECIO' or self.aux == 'FECHA-EVENTO' or              self.aux == 'HORA-EVENTO' or self.aux == 'EVENTO-LARGA-DURACION' or self.aux == 'CONTENT-URL-ACTIVIDAD' or self.aux == 'ID-EVENTO'):
                if(self.aux == 'TITULO'):
                    self.lista.append(self.evento)
                    self.evento = {}
                    self.evento['titulo'] = self.theContent 
                if(self.aux == 'TIPO'):
                    self.evento['tipo'] = self.theContent     
                if(self.aux == 'GRATUITO'):
                    self.evento['gratuito'] = self.theContent
                if(self.aux == 'PRECIO'):
                    self.evento['precio'] = self.theContent
                if(self.aux == 'FECHA-EVENTO'):
                    self.evento['fecha'] = fecha(self.theContent)
                if(self.aux == 'HORA-EVENTO'):
                    self.evento['hora'] = self.theContent
                if(self.aux == 'EVENTO-LARGA-DURACION'):
                    self.evento['duracion'] = self.theContent
                if(self.aux == 'CONTENT-URL-ACTIVIDAD'):
                    self.evento['url'] = self.theContent
                if(self.aux == 'ID-EVENTO'):
                    self.evento['id'] = self.theContent
        if self.inContent:
            self.inContent = 0
            self.theContent = ""
    def characters (self, chars):
        if self.inContent:
            self.theContent = self.theContent + chars
            
def xml():
    Parser = make_parser()
    Handler = CounterHandler()
    Parser.setContentHandler(Handler)
    xmlFile = urllib2.urlopen("http://datos.madrid.es/portal/site/egob/menuitem.ac61933d6ee3c31cae77ae7784f1a5a0/?vgnextoid=00149033f2201410VgnVCM100000171f5a0aRCRD&format=xml&file=0&filename=206974-0-agenda-eventos-culturales-100&mgmtid=6c0b6d01df986410VgnVCM2000000c205a0aRCRD")
    Parser.parse(xmlFile)
    return(Handler.lista)

lista = xml()

@csrf_exempt
def usuario(request,recurso):
    global formu
    salida = formu
    plantillaPost(request)
    miusuario = ''
    if request.user.is_authenticated():
        salida = "<ul class='bo effect1'> <h3>Eres " + request.user.username + "<br> Para salir pulsa " + "<a href= '/logout/" + recurso + "'>aqui</a></h3></ul> "
        miusuario = request.user  

    parseado = parseoPersonal(recurso)
    titulo1 = 'Esta es la página personal de ' + str(recurso) +  '. Aquí se muestran sus actividades seleccionadas.'
    renderizado = plantilla(salida, titulo1, parseado, '', '', miusuario )
    return HttpResponse(renderizado)

    

@csrf_exempt 
def logout_view(request,recurso):
        logout(request)
        if (recurso == '0'):
            return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/' + recurso)

def plantilla(contenido, titulo1, actividades, titulo2, parseo, user): 
    plantilla = get_template('index.html')
    c = Context({'contenido': contenido, 'actividades' : actividades, 'parseo' : parseo, 'titulo1' : titulo1, 'titulo2' : titulo2,'user':user })
    renderizado = plantilla.render(c)
    return renderizado

def plantillaPost(request):
    try:
        if request.method == "POST":
            username = request.POST['nombre']
            password = request.POST['contra']
            user = authenticate(username=username, password=password)
            try:
                Tabla.objects.get(user=username)
            except:
                usuario = Tabla()
                usuario.user = username
                usuario.save()
            if user is not None:
                if user.is_active:
                    login(request, user)
            return username
    except:
        return ''
@csrf_exempt 
def general(request):
    global formu
    salida=formu
    plantillaPost(request)
    miusuario = ''
    if request.user.is_authenticated():
        salida = "<ul class='bo effect1'> <h3>Eres " + request.user.username + "<br> Para salir pulsa " + "<a href='/logout/0'>aqui</a></h3></ul> "  
        miusuario = request.user
    usuarios = list(Tabla.objects.all())
    users = parseoUser(usuarios)
    parseado = parseo(lista, request)
    titulo1 = '¿Quieres venir a alguna actividad en Madrid? Aquí te mostramos las 10 próximas'
    titulo2 = '¿Quieres tener una página personal como estas que te mostramos? Para ello regístrate'
    renderizado = plantilla(salida,titulo1,parseado, titulo2, users, miusuario)
    return HttpResponse(renderizado)

def parseo(lista, request):
    salida = ''
    aux = []
    listaux = lista[1:]
    for fila in listaux:
        if (fila['fecha'][0] == '2014'):
            print fila['titulo']
            aux.append(fila)
    
    for i in ['01','02','03','04','05','06','07','08','09','10','11','12']:
        for j in ['01','02','03','04','05','06','07','08','09','10','11','12', '13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']:
            for fila in listaux:
                if(fila['fecha'][0] == '2015' and fila['fecha'][1] == i and fila['fecha'][2] == j and len(aux)<10):
                    aux.append(fila)             

    if request.user.is_authenticated():
        for fila in aux:
            i = lista.index(fila) 
            salida += '<p><h7><a class= rojo href=' + fila['url'] + '>~ ' + fila['titulo'] + '</a> </h7><br><a class= azul href=/add/' + str(i) + '/p' + '>Incluir a mi pagina personal</a></p><br>'
    else:
        for fila in aux:
            salida += '<p><h7><a class= rojo href=' + fila['url'] + '>~ ' + fila['titulo'] + '</a> </h7></p><br>'
    return salida
    
def parseoUser(listas):
    salida = ''
    for usuario in listas:
        if usuario.title == '':
            salida += '<p class= user>Esta es la pagina personal del usuario ' + usuario.user + ' de titulo <a class=azul href=/' + usuario.user + '>Pagina de ' + usuario.user +  '</a></p>'
        else:
            salida += '<p>Esta es la pagina personal del usuario ' + usuario.user + ' de titulo <a class=azul href=/' + usuario.user + '>' + usuario.title +  '</a></p>'

    return salida

def parseoPersonal(user):
    salida = ''
    actividades = list(Actividad.objects.filter(user=user))
    for actividad in actividades:
        salida += '<p><h7><a class = rojo href = /actividad/'+ actividad.ide + '>' + actividad.titulo + '</a></h7><br> lo celebraremos el ' + actividad.fecha +'<a class = azul href=/eliminar/' + actividad.ide + '/' + user + '> Eliminar actividad</a>' +'<a class = azul href=/actividad/' + actividad.ide +  '>    Pagina de la actividad</a> </p>'

    return salida

def add(request, recurso, recurso2):
    recurso = int(recurso)
    actividades = list(Actividad.objects.filter(user=request.user))
    aux = False
    if( len(list(Actividad.objects.all())) == 10):
        aux = True    
    for fila in actividades:
        if (fila.ide == lista[recurso]['id']):
            aux = True
    if(aux == False):
        act = Actividad()
        act.user = request.user
        act.titulo = lista[recurso]['titulo']
        act.tipo = lista[recurso]['tipo']
        try: 
            act.gratuito = int(lista[recurso]['gratuito'])
        except KeyError:
            act.precio = int(lista[recurso]['precio'])
        act.fecha = lista[recurso]['fecha'][2] + '/' + lista[recurso]['fecha'][1] + '/' + lista[recurso]['fecha'][0] 
        act.hora = lista[recurso]['hora']
        act.duracion = int(lista[recurso]['duracion'])
        act.url = lista[recurso]['url']
        act.ide = lista[recurso]['id']
        act.save()
    if (recurso2 == 'p'):
        return HttpResponseRedirect('/')
    else:
        aux= '/' + recurso2
        return HttpResponseRedirect(aux)         

def eliminar(request, recurso, user):
    if request.user.is_authenticated():
        actividades = list(Actividad.objects.filter(user=request.user))
        for fila in actividades:
            if (fila.ide == recurso):
                fila.delete()
    return HttpResponseRedirect('/' + str(user))

@csrf_exempt 
def ayuda(request):
    global formu
    formu1 = formu
    titulo1 = 'Página de ayuda de la web'
    miusuario = ''
    plantillaPost(request)
    if request.user.is_authenticated():
        formu1 = "<ul class='bo effect1'> <h3>Eres " + request.user.username + "<br> Para salir pulsa " + "<a href= '/logout/ayuda'>aqui</a></h3></ul> "
        miusuario = request.user

    ayuda = '<p class=user>En la primera parte de la página principal se muestran las 10 actividades más próximas en el tiempo.</p><p class=user> En la parte inferior de la página aparecen las cuentas de usuarios.</p><p class=user>Para poder obtener una cuenta deberás loguearte y estar registrado.</p><p class=user>Para añadir una actividad a tu cuenta, deberás seleccionar la actividad que desees y pulsar en "Incluir a mi página personal" estando logueado.</p><p class=user>Para eliminar una actividad deberás meterte en tu cuenta y pulsar "Eliminar actividad"</p>'
    renderizado = plantilla(formu1,titulo1,ayuda, '', '', miusuario)
    return HttpResponse(renderizado)
 
@csrf_exempt    
def todas(request):
    global formu
    formu1 = formu
    plantillaPost(request)
    salida=''
    contador = 0
    miusuario = ''
    if request.user.is_authenticated():
        formu1 = "<ul class='bo effect1'> <h3>Eres " + request.user.username + "<br> Para salir pulsa " + "<a href= '/logout/todas'>aqui</a></h3></ul> "
        miusuario = request.user
    formu2 =  "<form class = 'formu2' action='' method='POST'><h2>Filtra según:</h2><button class='submit'></button><input type='text' name='titulo' placeholder='TÍTULO                ej: La ciudad encantada '/><input type='text' name='fecha'placeholder='FECHA                 ej: 29/05/2015'/><input type='text' name='duracion'placeholder='DURACIÓN        ej: larga'/><input type='text' name='precio'placeholder='GRATIS                 ej: si'/></form>"
    aux= True
    listaux = lista[1:]
    listaux2 = lista[1:]
    listaux3 = []
    try:
        if request.method == "POST":
            titulo = request.POST['titulo']
            fecha = request.POST['fecha']
            duracion = request.POST['duracion']
            gratis = request.POST['precio']
            
            if (titulo != ''):
                aux= False
                for fila in listaux2:
                    if (titulo in fila['titulo']): 
                        contador += 1
                        try:
                            salida += '<p><a class= rojo href=' + fila['url'] + '>~ ' + fila['titulo'] + '</a><br><a class= azul href=/add/' + str(contador) + '/todas'+ '>Incluir a mi pagina personal</a></p>'
                        except KeyError:
                            salida += '<p>~ ' + fila['titulo'] + '</a><br><a class= azul href=/add/' + str(contador) + '/todas'+ '>Incluir a mi pagina personal</a></p>'
                    else:
                        ubicacion = listaux.index(fila) 
                        del listaux[ubicacion] 

            listaux2 = listaux[:]
            if (duracion != ''):
                aux= False
                if (duracion == 'larga'):
                    duracion = '1'
                elif(duracion == 'corta'):
                    duracion = '0'
                salida=''
                contador=0
                for fila in listaux2: 
                    if not(duracion == fila['duracion']):
                        ubicacion = listaux.index(fila) 
                        del listaux[ubicacion]     
                for fila in listaux:
                    contador += 1
                    try:
                        salida += '<p><a class= rojo href=' + fila['url'] + '>~ ' + fila['titulo'] + '</a><br><a class= azul href=/add/' + str(contador) + '/todas'+ '>Incluir a mi pagina personal</a></p>'
                    except KeyError:
                        salida += '<p>~ ' + fila['titulo'] + '</a><br><a class= azul href=/add/' + str(contador) + '/todas'+ '>Incluir a mi pagina personal</a></p>' 
                         
            listaux2 = listaux[:]
            if(gratis != ''):
                aux=False
                if (gratis == 'si'):
                    gratis = '1'
                elif(gratis == 'no'):
                    gratis = '0'     
                salida=''
                contador=0
                for fila in listaux2: 
                    if not(gratis == fila['gratuito']):
                        ubicacion = listaux.index(fila) 
                        del listaux[ubicacion]     
                for fila in listaux:
                    contador += 1
                    try:
                        salida += '<p><a class= rojo href=' + fila['url'] + '>~ ' + fila['titulo'] + '</a><br><a class= azul href=/add/' + str(contador) + '/todas'+ '>Incluir a mi pagina personal</a></p>'
                    except KeyError:
                        salida += '<p>~ ' + fila['titulo'] + '</a><br><a class= azul href=/add/' + str(contador) + '/todas'+ '>Incluir a mi pagina personal</a></p>'   
    except:
        salida=''
    if (aux):
        for fila in listaux2:
            try:
                contador += 1
                salida+=  '<p><a class= rojo href=' + fila['url'] + '>~ ' + fila['titulo'] + '</a><br><a class= azul href=/add/' + str(contador) + '/todas'+ '>Incluir a mi pagina personal</a></p>'
            except KeyError:
                contador += 1
                salida += '<p>~ ' + fila['titulo'] + '</a><br><a class= azul href=/add/' + str(contador) + '/todas'+ '>Incluir a mi pagina personal</a></p>'

    titulo= "<p class = user>Se muestran un total de " + str(contador) + ' actividades de ocio y cultura' + salida + '</p>'
    renderizado = plantilla(formu1,formu2,titulo, '', '', miusuario )
    return HttpResponse(renderizado)

@csrf_exempt 
def actividad(request,recurso):
    global formu
    salida=formu
    plantillaPost(request)
    miusuario = ''
    if request.user.is_authenticated():
        salida = "<ul class='bo effect1'> <h3>Eres " + request.user.username + "<br> Para salir pulsa " + "<a href=/logout/actividad/" + recurso + ">aqui</a></h3></ul> " 
        miusuario = request.user 
    actividad = ''
    precio = ''
    listaux = lista[1:] 
    for fila in listaux:
        print fila
        if (fila['id'] == recurso):
            actividad = fila  
    gratuito = actividad['gratuito']
    if(gratuito == '1'):
        precio= '. La actividad es gratuita '
    else:
        try:
            dinero = actividad['precio']
            precio = 'La actividad vale' + dinero
        except KeyError:
            precio= '. La actividad no es gratuita '

    duracion = actividad['duracion']
    if(duracion == '1'):
        dura = 'larga duracion '
    else:
        dura = 'corta duracion. '

    
    titulo1 = 'Esta es la pagina de la actividad ' + actividad['titulo']
    parseado = '<p class=user>' + actividad['titulo'] + ' es una actividad que se hara o se lleva haciendo desde el ' + actividad['fecha'][2] + '/' + actividad['fecha'][1] + '/' + actividad['fecha'][0] + ' a las ' + actividad['hora']+ ' horas. Es de tipo ' + actividad['tipo'] + str(precio) + 'y es de ' + str(dura) + '<br>Para mas informacion pulse <a href='+ actividad['url'] +'>aqui</a></p>'
    renderizado = plantilla(salida,titulo1,parseado, '', '',miusuario)
    return HttpResponse(renderizado)
