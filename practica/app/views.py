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
from models import Like
import time
from xml.dom import minidom


class Estilo(object): 
    letra = "" 
    color = "" 
    fondo = ""

banner = Estilo()
menu = Estilo()
formul = Estilo()
pie = Estilo()

formu = "<form class = 'uno' action='' method='POST'><h2><span class='entypo-login'></span>Loguéate</h2><button class='submit'><span class='entypo-lock'></span></button><span class='entypo-user inputUserIcon'></span><input type='text' class='user' name='nombre'placeholder='ursername'/><span class='entypo-key inputPassIcon'></span><input type='password' name='contra' class='pass'placeholder='password'/></form>"

fechas = ''


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
        elif name == 'atributo':
            self.aux = normalize_whitespace(attrs.get('nombre')) 
            if(self.aux == 'TITULO' or self.aux == 'TIPO' or self.aux == 'GRATUITO' or self.aux == 'PRECIO' or self.aux == 'FECHA-EVENTO' or              self.aux == 'HORA-EVENTO' or self.aux == 'EVENTO-LARGA-DURACION' or self.aux == 'CONTENT-URL' or self.aux == 'ID-EVENTO'):
                self.inContent = 1
        
            
    def endElement (self, name):
        if self.inContent:
            self.theContent = normalize_whitespace(self.theContent)
        if name == 'atributo':
            if(self.aux == 'TITULO' or self.aux == 'TIPO' or self.aux == 'GRATUITO' or self.aux == 'PRECIO' or self.aux == 'FECHA-EVENTO' or              self.aux == 'HORA-EVENTO' or self.aux == 'EVENTO-LARGA-DURACION' or self.aux == 'CONTENT-URL' or self.aux == 'ID-EVENTO'):
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
                if(self.aux == 'CONTENT-URL'):
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
    formu2 =  ''
    titulo1 = ''
    titulo = ''
    descripcion = ''
    fila = Tabla.objects.get(user=recurso)
    if request.method == "POST":
        try:
            titulo = request.POST['titulo']
            descripcion = request.POST['descripcion'] 
        except:
            print 'ok'
    if(titulo != ''):
        fila.title = titulo
        fila.save()
    if(descripcion != ''):
        fila.descripcion = descripcion
        fila.save()

    miusuario = ''
    
    parseado = parseoPersonal(recurso)

    if request.user.is_authenticated():
        salida = "<ul class='bo effect1'> <h3>Eres " + request.user.username + "<br> Para salir pulsa " + "<a href= '/logout/" + recurso + "'>aqui</a></h3></ul> "
        formu2 =  "<form class = 'formu3' action='' method='POST'><h2>Cambia valores</h2><button class='submit'></button><input type='text' name='titulo' placeholder='TÍTULO DE PÁGINA'/><input type='text' name='descripcion' placeholder='DESCRIPCIÓN DE PÁGINA'/><input type='text' name='letra' placeholder='LETRA            ej: georgia '/><input type='text' name='color'placeholder='Color                ej: red'/><input type='text' name='fondo' placeholder='Fondo               ej: blue'/><input type='text' name='sitio'placeholder='LUGAR           ej: banner/menu/formulario/pie'/></form>"
        miusuario = request.user
        if(fila.title == ''):
            titulo1 = '<p class = user> Esta es la pagina personal de ' + str(recurso) + ' de titulo: Pagina de '+ fila.user +  '.<br><a href=/' + fila.user + '/rss>Canal RSS<br></a> Aqui se muestran sus actividades seleccionadas.</p>' + parseado 
        else:        
            titulo1 = '<p class = user> Esta es la pagina personal de ' + str(recurso) + ' de titulo: '+ fila.title +  '.<br><a href=/' + fila.user + '/rss>Canal RSS<br></a> Aqui se muestran sus actividades seleccionadas.</p>' + parseado  
    else:
        titulo1 = '<p class = user> Esta es la pagina personal de ' + str(recurso) +  '.<br><a href=/' + fila.user + '/rss>Canal RSS<br></a> Aqui se muestran sus actividades seleccionadas.</p>' + parseado
    
    css = cambioCss(request)
    plantilla = get_template('index.html')
    
    c = Context({'contenido': salida, 'actividades' : titulo1, 'parseo' : '', 'titulo1' : formu2, 'titulo2' : '', 'user': miusuario, 'css':css })
    renderizado = plantilla.render(c)
    
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
    
    c = Context({'contenido': contenido, 'actividades' : actividades, 'parseo' : parseo, 'titulo1' : titulo1, 'titulo2' : titulo2,'user': user })
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
    parseado = parseo(lista, request,'')
    titulo1 = '¿Quieres venir a alguna actividad en Madrid? Aquí te mostramos las 10 próximas'
    titulo2 = '¿Quieres tener una página personal como estas que te mostramos? Para ello regístrate'
    renderizado = plantilla(salida,titulo1,parseado, titulo2, users, miusuario)
    return HttpResponse(renderizado)

def parseo(lista, request, lugar):
    salida = ''
    aux = []
    listaux = lista[1:]
    for fila in listaux:
        if (fila['fecha'][0] == '2014'):
            aux.append(fila)
    
    for i in ['01','02','03','04','05','06','07','08','09','10','11','12']:
        for j in ['01','02','03','04','05','06','07','08','09','10','11','12', '13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']:
            for fila in listaux:
                if(fila['fecha'][0] == '2015' and fila['fecha'][1] == i and fila['fecha'][2] == j and len(aux)<10):
                    aux.append(fila)             

    gustas = ''
    if request.user.is_authenticated():
        
        for fila in aux:
            i = lista.index(fila)
            try:
                
                gustas = Like.objects.get(actividad = i)
                print 'busco try '+ str(i)
                gustas = gustas.like
            except :
                gustas= 0
            
            salida += '<p><h7><a class= rojo href=' + fila['url'] + '>~ ' + fila['titulo'] + '</a> </h7><br><a class= azul href=/add/' + str(i) + '/29>Incluir a mi pagina personal</a><a class= azul href=/like/0/' + str(i) + '> Sumar un me gusta: ' + str(gustas) + '</a></p><br>'
    else:
        for fila in aux:
            i = lista.index(fila)
            try:
                
                gustas = Like.objects.get(actividad = i)
                print 'busco try '+ str(i)
                gustas = gustas.like
            except :
                gustas= 0
            salida += '<p><h7><a class= rojo href=' + fila['url'] + '>~ ' + fila['titulo'] + '</a> </h7><br><a class= azul href=/like/0/' + str(i) + '> Sumar un me gusta: ' + str(gustas) + '</a></p><br>'
    return salida

@csrf_exempt 
def megustas(request,lugar,recurso):

    gustas = ''
    try:
        gustas = Like.objects.get(actividad = int(recurso))
        gustas.like += 1
        gustas.save()
        print 'try ' + recurso
    except :
        print 'except ' + recurso
        gustas = Like()
        gustas.like=1
        gustas.actividad = int(recurso)
        gustas.save()

    if(lugar == '1'): 
        return HttpResponseRedirect('/todas')

    elif(lugar == '0'): 
        return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/actividad/' + lugar)   
     
    
def parseoUser(listas):
    salida = ''
    for usuario in listas:
        if usuario.title == '':
            salida += '<p class = user>Esta es la pagina personal del usuario ' + usuario.user + ' de titulo <a class=azul href=/' + usuario.user + '>Pagina de ' + usuario.user +  '</a>'
        else:
            salida += '<p class = user>Esta es la pagina personal del usuario ' + usuario.user + ' de titulo <a class=azul href=/' + usuario.user + '>' + usuario.title +  '</a>'
        if usuario.descripcion != '':
            salida += '<br>Cuya descripcion es: ' + usuario.descripcion +'</p>'
        else:
            salida += '</p>'

    return salida

def parseoPersonal(user):
    salida = ''
    actividades = list(Actividad.objects.filter(user=user))
    for actividad in actividades:
        salida += '<p><h7><a class = rojo href = /actividad/'+ actividad.ide + '>' + actividad.titulo + '</a></h7><br> lo celebraremos el ' + actividad.fecha +'<a class = azul href=/eliminar/' + actividad.ide + '/' + user + '> Eliminar actividad</a>' +'<a class = azul href=/actividad/' + actividad.ide +  '>    Pagina de la actividad</a> </p>'

    return salida

@csrf_exempt 
def add(request, recurso1):
    recurso = int(recurso1.split('/')[0])
    #recurso = recurso1.split('/')[0]
    print 'recurso' + str(recurso)
    i=1;
    longi= len(recurso1.split('/')[1:])
    recurso2 = '/'
    
    while (i<= longi):        
        recurso2 += '/' + recurso1.split('/')[i]
        i+=1
    print recurso2
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
    if (recurso2 == '//29'):
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

    ayuda = '<p class=user>En la primera parte de la página principal se muestran las 10 actividades más próximas en el tiempo.</p><p class=user> En la parte inferior de la página aparecen las cuentas de usuarios.</p><p class=user>Para poder obtener una cuenta deberás loguearte y estar registrado.</p><p class=user>Para añadir una actividad a tu cuenta, deberás seleccionar la actividad que desees y pulsar en "Incluir a mi página personal" estando logueado.</p><p class=user>Para eliminar una actividad deberás meterte en tu cuenta y pulsar "Eliminar actividad"</p><p class=user>En la página "todas" podemos buscar conforme a nuestras preferencias. Si queremos buscar por título, debemos añadir el título completo de la actividad o parte de él. Si lo que queremos es buscar por fecha, deberá tener el formato dd/mm/aaaa. Si deseamos filtrar por duración, deberemos hacerlo poniendo corta o larga. Si finalmente queremos hacerlo por su precio, se deberá poner "si" para ver las actividades gratuitas y "no" para ver las que son de pago.<br><br>Seguidamente aparecerán las actividades seleccionadas por los usuarios y un botón para actualizar las actividades (siempre y cuando estés logueado). Por otro lado, aparecerán las actividades según las preferencias expuestas anteriormente. </p><p class = user>Si estás logueado podrás acceder a tu página personal pulsando "personal" en el menú. Si no lo estás, podrás acceder a una página personal pinchando en el título de las páginas personales que se encuentran en la parte inferior de la página principal, o bien introduciendo en la url como recurso, el usuario de la página que quieras ver.</p><p class = user>Una vez que estés en una página personal, si no estás logueado aparecerá un enlace al canal RSS del usuario y sus actividades seleccionadas. Si estás logueado, aparecerá un formulario en el que podrás cambiar el título de la página y la descripción de la misma. Por otro lado podrás modificar el tipo de letra, el color de esta y el fondo de uno de los cuatro sitios que aparecen en el formulario y siguiendo las instrucciones que se dan en el mismo. Si quieres volver al estado original deberás introducir un espacio en el apartado que desees.</p>'
    renderizado = plantilla(formu1,titulo1,ayuda, '', '', miusuario)
    return HttpResponse(renderizado)

@csrf_exempt
def cambioCss(request):
    global banner
    global menu 
    global formu 
    global pie

    try:
        if request.method == "POST":
            letra = request.POST['letra']
            color = request.POST['color']
            fondo = request.POST['fondo']
            sitio = request.POST['sitio']

        css = ''
        if sitio != '':
            if sitio == 'pie':
                if letra != '':
                    pie.letra = letra
                if color != '':
                    pie.color = color
                if fondo != '':
                    pie.fondo = fondo
            if sitio == 'banner':
                if letra != '':
                    banner.letra = letra
                if color != '':
                    banner.color = color
                if fondo != '':
                    banner.fondo = fondo
            if sitio == 'menu':
                if letra != '':
                    menu.letra = letra
                if color != '':
                    menu.color = color
                if fondo != '':
                    menu.fondo = fondo
            if sitio == 'formulario':
                if letra != '':
                    formul.letra = letra
                if color != '':
                    formul.color = color
                if fondo != '':
                    formul.fondo = fondo
            
    except:
        css = ''

    css = '#footer{font-family:' + pie.letra + '; color:' + pie.color + '; background:' + pie.fondo + ';}' 
    css += '#menu{background:' + menu.fondo + ';}' 
    css += '#menu ul li a{font-family:' + menu.letra + '; color:' + menu.color + ';}'
    css += '#headerpic{font-family:' + banner.letra + '; color:' + banner.color + '; background:' + banner.fondo + ';}'
    css += 'form.uno h2{font-family:' + formul.letra + '; color:' + formul.color + '; background:' + formul.fondo + ';}'
    css += 'form.uno{background:' + formul.fondo + ';}'
    css += '.bo h3{font-family:' + formul.letra + '; color:' + formul.color + '; }'
    css += '.bo h3 a{font-family:' + formul.letra + '; color:' + formul.color +  ';}'
    css += '.bo{background:' + formul.fondo + ';}'

    return css 

 
@csrf_exempt    
def todas(request,recurso):
    
    global formu
    formu1 = formu
    global fechas
    fechas = fechas
    plantillaPost(request)
    salida=''
    contador = 0
    miusuario = ''
    formu2 =  "<form class = 'formu2' action='' method='POST'><h2>Filtra según:</h2><button class='submit'></button><input type='text' name='titulo' placeholder='TÍTULO                ej: La ciudad encantada '/><input type='text' name='fecha'placeholder='FECHA                 ej: 29/05/2015'/><input type='text' name='duracion'placeholder='DURACIÓN        ej: larga'/><input type='text' name='precio'placeholder='GRATIS                 ej: si'/></form>"
    aux= True

    if request.user.is_authenticated():
        formu1 = "<ul class='bo effect1'> <h3>Eres " + request.user.username + "<br> Para salir pulsa " + "<a href= '/logout/todas'>aqui</a></h3></ul> "
        miusuario = request.user  
    
    if(recurso == '/actualizar'):
        lista2 = xml()
        fechas = time.strftime("%d/%m/%y")
        listaux = lista2[1:]
        listaux2 = lista2[1:]
    else:
        listaux = lista[1:]
        listaux2 = lista[1:]

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

            listaux2 = listaux[:]

            if(fecha != ''):
                aux=False
                fecha = fecha.split('/')     
                salida=''
                contador=0
                for fila in listaux2: 
                    if not(fecha[2] == fila['fecha'][0] and fecha[1] == fila['fecha'][1] and fecha[0] == fila['fecha'][2]):
                        ubicacion = listaux.index(fila) 
                        del listaux[ubicacion]
                    else: 
                        print   fila['fecha'][2] + fila['fecha'][1] + fila['fecha'][0]   
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
            i = lista.index(fila)
            try:                
                gustas = Like.objects.get(actividad = i)
                gustas = gustas.like
            except :
                gustas= 0

            try:
                contador += 1
                salida+=  '<p><a class= rojo href=' + fila['url'] + '>~ ' + fila['titulo'] + '</a><br><a class= azul href=/add/' + str(contador) + '/todas'+ '>Incluir a mi pagina personal</a><a class= azul href=/like/1/' + str(i) + '> Sumar un me gusta: ' + str(gustas) + '</a></p>'
            except KeyError:
                contador += 1
                salida += '<p>~ ' + fila['titulo'] + '</a><br><a class= azul href=/add/' + str(contador) + '/todas'+ '>Incluir a mi pagina personal</a><a class= azul href=/like/1/' + str(i) + '> Sumar un me gusta: ' + str(gustas) + '</a></p>'

    if request.user.is_authenticated():
        todas = ''
        actividades = list(Actividad.objects.all())
        conta = 0        
        for fila in actividades:
            for acti in lista[1:]:
                if(acti['id'] == fila.ide):
                    conta = lista.index(acti)
                    todas += '<a class = rojo href='+ lista[conta]['url'] + '>' + lista[conta]['titulo'] + '</a><br><a class= azul href=/add/' + str(conta) + '/actividad/' + lista[conta]['id'] + '>Incluir a mi pagina personal</a></br>'
        titulo= "<p class = user>Se muestran un total de " + str(contador) + ' actividades de ocio y cultura' + '</p><p>Actualizado por ultima vez el' + str(fechas) + '<a class button href =/todas/actualizar> Actualizar actividades</a></p><p>'+ salida + '</p>'
        
        formu1 += "<p class = user>Lista de actividades disponibles seleccionadas por los usuarios<br>" + todas +"</p>"
    else:
        titulo= "<p class = user>Se muestran las actividades de ocio y cultura</p><p>" + salida + '</p>'
            
    renderizado = renderizado = plantilla(formu1,formu2,titulo, '', '', miusuario )    
    return HttpResponse(renderizado)


def parseoAdicional(url):
    xmlFile = urllib2.urlopen(url)
    try:
        c = xmlFile.read().split('parrafo">')[1]
        c = c.split('</div>')[0]
    except:
        c = ''     
    return c.decode('utf-8')

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
        if (fila['id'] == recurso):
            print 'entraa'
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
    
    i = lista.index(actividad)
    try:
        
        gustas = Like.objects.get(actividad = i)
        print 'busco try '+ str(i)
        gustas = gustas.like
    except :
        gustas= 0
    adicional = parseoAdicional(actividad['url'])
    titulo1 = 'Esta es la pagina de la actividad ' + actividad['titulo']
    parseado = '<p class=user>' + actividad['titulo'] + ' es una actividad que se hara o se lleva haciendo desde el ' + actividad['fecha'][2] + '/' + actividad['fecha'][1] + '/' + actividad['fecha'][0] + ' a las ' + actividad['hora']+ ' horas. Es de tipo ' + actividad['tipo'] + str(precio) + 'y es de ' + str(dura) + '<br>Para mas informacion pulse <a href='+ actividad['url'] +'>aqui</a><br>Informacion adicional: <br>' + adicional+ '</p><p><a class= azul href=/like/' + recurso +'/' + str(i) + '> Sumar un me gusta: ' + str(gustas) + '</a></p>'
    renderizado = plantilla(salida,titulo1,parseado, '', '', miusuario)
    return HttpResponse(renderizado)

@csrf_exempt 
def rss(request, recurso):
    global formu
    salida=formu
    plantillaPost(request)
    miusuario = ''
    if request.user.is_authenticated():
        salida = "<ul class='bo effect1'> <h3>Eres " + request.user.username + "<br> Para salir pulsa " + "<a href=/logout/" + recurso + "/rss>aqui</a></h3></ul> " 
        miusuario = request.user
    parseo = ''
    duracion = ''
    dinero = ''
    precio = ''
    actividades = list(Actividad.objects.filter(user=recurso))
    for actividad in actividades:
        if(actividad.duracion == '1'):
            duracion = 'Larga duracion '
        else:
            duracion = 'Corta duracion '
        if(actividad.gratuito == '1'):
            precio= ' La actividad es gratuita '
        else:
            if actividad.precio != None :
                precio = 'La actividad vale' + actividad.precio
            else:
                precio= 'La actividad no es gratuita '
        parseo += '<p><item><strong><titulo>'+ actividad.titulo +'</titulo></strong><br><tipo>' + actividad.tipo + '</tipo><br><fecha>' + actividad.fecha + '</fecha><br><hora>' + actividad.hora + '</hora><br><duracion>' + duracion + '</duracion><br><precio>' + precio + '</precio></item></p>' 
             
    contenido = '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>' + parseo + '</channel>'    
    renderizado = plantilla(salida,'Canal RSS',contenido, '', '', miusuario)
    return HttpResponse(renderizado)

# rss mirar github y css moreno
