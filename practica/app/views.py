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

#maximo 10 en pagina usuario
def normalize_whitespace(text):
    return string.join(string.split(text), ' ')

    
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
                    self.evento['fecha'] = self.theContent
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
        else:
                salida = "<form action='' method='POST'><h2><span class='entypo-login'></span>Datos incorrectos</h2><button class='submit' ><span class='entypo-lock'></span></button><span class='entypo-user inputUserIcon'></span><input type='text' class='user' name='nombre'placeholder='ursername'/><span class='entypo-key inputPassIcon'></span><input type='password' name='contra' class='pass'placeholder='password'/></form>"

    if request.user.is_authenticated():
        salida = "<ul class='bo effect1'> <h3>Eres " + request.user.username + "<br> Para salir pulsa " + "<a href= '/logout/" + recurso + "'>aqui</a></h3></ul> "  
    else:
        salida = "<form action='' method='POST'><h2><span class='entypo-login'></span>Loguéate</h2><button class='submit'><span class='entypo-lock'></span></button><span class='entypo-user inputUserIcon'></span><input type='text' class='user' name='nombre'placeholder='ursername'/><span class='entypo-key inputPassIcon'></span><input type='password' name='contra' class='pass'placeholder='password'/></form>"

    parseado = parseoPersonal(recurso)
    titulo1 = 'Esta es la página personal de ' + str(recurso) +  '. Aquí se muestran sus actividades seleccionadas.'
    plantilla = get_template('index.html')
    c = Context({'contenido': salida, 'actividades' : parseado, 'titulo1' : titulo1, })
    renderizado = plantilla.render(c)
    return HttpResponse(renderizado)

    

@csrf_exempt 
def logout_view(request,recurso):
        logout(request)
        if (recurso == 0):
            return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/' + recurso)
        
@csrf_exempt 
def general(request):
    salida = "<form action='' method='POST'><h2><span class='entypo-login'></span>Loguéate</h2><button class='submit'><span class='entypo-lock'></span></button><span class='entypo-user inputUserIcon'></span><input type='text' class='user' name='nombre'placeholder='ursername'/><span class='entypo-key inputPassIcon'></span><input type='password' name='contra' class='pass'placeholder='password'/></form>"

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
        else:
                salida = "<form action='' method='POST'><h2><span class='entypo-login'></span>Datos incorrectos</h2><button class='submit' ><span class='entypo-lock'></span></button><span class='entypo-user inputUserIcon'></span><input type='text' class='user' name='nombre'placeholder='ursername'/><span class='entypo-key inputPassIcon'></span><input type='password' name='contra' class='pass'placeholder='password'/></form>"

    if request.user.is_authenticated():
        salida = "<ul class='bo effect1'> <h3>Eres " + request.user.username + "<br> Para salir pulsa " + "<a href='/logout/0'>aqui</a></h3></ul> "   

    usuarios = list(Tabla.objects.all())
    users = parseoUser(usuarios)
    #lista = xml()
    parseado = parseo(lista, request)
    titulo1 = '¿Quieres venir a alguna actividad en Madrid? Aquí te mostramos las 10 próximas'
    titulo2 = '¿Quieres tener una página personal como estas que te mostramos? Para ello regístrate'
    plantilla = get_template('index.html')
    c = Context({'contenido': salida, 'actividades' : parseado, 'parseo' : users, 'titulo1' : titulo1, 'titulo2' : titulo2, })
    renderizado = plantilla.render(c)
    return HttpResponse(renderizado)



def parseo(lista, request):
    salida = ''
    bucle=[1,2,3,4,5,6,7,8,9,10]
    if request.user.is_authenticated():
        for i in bucle:
            #salida += '<p><h7>' + lista[i]['titulo'] + '</h7><a href=/add/' + str(i) + '>Incluir a mi página personal</a></p>'
            salida += '<p><h7>' + lista[i]['titulo'] + '</h7>. Para encontrar mas informacion <a href=' + lista[i]['url'] + '>Pulse este enlace</a> <a href=/add/' + str(i) + '>Incluir a mi pagina personal</a></p>'
    else:
        for i in bucle:
            #salida += '<p><h7>' + lista[i]['titulo'] + '</h7> lo celebraremos el ' + lista[i]['fecha'] +' a las ' + lista[i]['hora'] + '. Para encontrar mas informacion <a href=' + lista[i]['url'] + '>Pulse este enlace</a> </p>'
            salida += '<p><h7>' + lista[i]['titulo'] + '</h7>. Para encontrar mas informacion <a href=' + lista[i]['url'] + '>Pulse este enlace</a> </p>'
    return salida
    
def parseoUser(listas):
    salida = ''
    for usuario in listas:
        if usuario.title == '':
            salida += '<p>Esta es la pagina personal del usuario ' + usuario.user + ' de titulo <a href=/' + usuario.user + '>Pagina de ' + usuario.user +  '</a></p>'
        else:
            salida += '<p>Esta es la pagina personal del usuario ' + usuario.user + ' de titulo <a href=/' + usuario.user + '>' + usuario.title +  '</a></p>'

    return salida

def parseoPersonal(user):
    salida = ''
    actividades = list(Actividad.objects.filter(user=user))
    for actividad in actividades:
        salida += '<p><h7>' + actividad.titulo + '</h7> lo celebraremos el ' + actividad.fecha +' a las ' + actividad.hora + '. Para encontrar mas informacion <a href=/actividad/id>Pulse este enlace</a><a href=/eliminar/' + actividad.ide + '/' + user + '> Eliminar actividad</a> </p>'

    return salida

def add(request, recurso):
    recurso = int(recurso)
    actividades = list(Actividad.objects.filter(user=request.user))
    aux = False
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
        act.fecha = lista[recurso]['fecha']
        act.hora = lista[recurso]['hora']
        act.duracion = int(lista[recurso]['duracion'])
        act.url = lista[recurso]['url']
        act.ide = lista[recurso]['id']
        act.save()
    return HttpResponseRedirect('/')

def eliminar(request, recurso, user):
    if request.user.is_authenticated():
        actividades = list(Actividad.objects.filter(user=request.user))
        for fila in actividades:
            if (fila.ide == recurso):
                fila.delete()
    return HttpResponseRedirect('/' + str(user))
    
