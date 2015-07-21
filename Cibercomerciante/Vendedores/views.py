import json
from django.template import RequestContext
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from models import *
from Gestion.models import *
from django.core import serializers
from django.core.files import File
import re
import time
from django.contrib.auth.decorators import user_passes_test  
# Create your views here.
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.models import User


 
'''
Autor 			Jhonatan Acelas Arevalo
Fecha 	 		11 Julio 2015
Descripcion  	Renderiza la pantalla de inicio de vendedor
Funcion 		Vendedores.1
Modifico
'''


@login_required(login_url='/logearse')
def baseVendedor(request):
	return render_to_response('BaseVendedores.html',locals(), context_instance=RequestContext(request))



@login_required(login_url='/logearse')
def inicioVendedorCatalogo(request):
	if catalogoVendedor(request):
		productos = Producto.objects.all()
		categorias = CategoriaProducto.objects.all()
		subcategorias = CategoriaInterna.objects.all()
		return render_to_response('Perfil_vendedores_catalogo.html',locals(), context_instance=RequestContext(request))
	return HttpResponseRedirect('/')

@login_required(login_url='/logearse')
def inicioVendedorPedidos(request):
	if pedidosVendedor(request):
		return render_to_response('Perfil_vendedores_pedidos.html',locals(), context_instance=RequestContext(request))
	return HttpResponseRedirect('/')

@login_required(login_url='/logearse')
def inicioVendedorReportes(request):
	if reportesVendedor(request):
		return render_to_response('Perfil_vendedores_reportes.html',locals(), context_instance=RequestContext(request))
	return HttpResponseRedirect('/')

@login_required(login_url='/logearse')
def inicioVendedorUsuarios(request):
	if usuariosVendedor(request):
		admin =  Usuario.objects.get(user=request.user)
		usuarios = Usuario.objects.filter(empresa=admin.empresa)
		return render_to_response('Perfil_vendedores_usuarios.html',locals(), context_instance=RequestContext(request))		
	return HttpResponseRedirect('/')

'''
Autor 			Jhonatan Acelas Arevalo 
Fecha 	 		20 Julio 2015
Descripcion  	agregar usuarios
Funcion 		Vendedores.1
'''

@login_required(login_url='/logearse')
def agregar_usuariov(request):
	if usuariosVendedor(request):
		return render_to_response('Agregar_usuario_vendedores.html',locals(), context_instance=RequestContext(request))		
	return HttpResponseRedirect('/')


'''
Autor 			Jhonatan Acelas Arevalo 
Fecha 	 		20 Julio 2015
Descripcion  	agregar usuarios
Funcion 		Vendedores.1
'''

@login_required(login_url='/logearse')
def guardarUsuarioV(request):
	if usuariosVendedor(request):
		if request.method == 'POST':
			try:
				existe = User.objects.get(username=request.POST['username'])
				mensaje= "el usuario ya existe"
				return HttpResponseRedirect('/agregar_usuariov/')
			except Exception, e:
				user = User.objects.create_user(request.POST['username'],None,request.POST['password'])
				user.first_name=request.POST['nombres']
				user.last_name=request.POST['apellidos']
				user.email=request.POST['email']
				user.is_active = True
				user.save()
				if  'administrador' in  request.POST:
					g = Group.objects.get(name='AV')
					g.user_set.add(user)
				else :
					if  'catalogo' in request.POST:
						g = Group.objects.get(name='CV')
						g.user_set.add(user)
					if  'pedidos' in request.POST:
						g = Group.objects.get(name='PV')
						g.user_set.add(user)
					if  'reportes' in request.POST:
						g = Group.objects.get(name='RV')
						g.user_set.add(user)

				admin =  Usuario.objects.get(user=request.user)
				# guardamos cybercomerciante
				cybercomerciante = Usuario(user=user,empresa=admin.empresa)
				cybercomerciante.save()
				#guardamos los permisos la base de atos
				tipo_usuario =  TipoUsuario.objects.get(nombre_tipo_usuario='AC')
				permisos =  Permisos(usuario=cybercomerciante,tipo_usuario=tipo_usuario)
				permisos.save()
			return HttpResponseRedirect('/inicioVendedorUsuarios/')
	return HttpResponseRedirect('/')

'''
Autor 			Jhonatan Acelas Arevalo 
Fecha 	 		20 Julio 2015
Descripcion  	agregar usuarios
Funcion 		Vendedores.1
'''

@login_required(login_url='/logearse')
def eliminarUsuario(request):
	if usuariosVendedor(request):
		if request.method == 'POST':
			d = User.objects.get(username=request.POST['pk_eliminar']).delete()
		return HttpResponseRedirect('/inicioVendedorUsuarios/')
	return HttpResponseRedirect('/')


'''
Autor 			Sebastian Rincon Rangel 
Fecha 	 		13 Julio 2015
Descripcion  	Renderiza las pantallas de de gestion de catalogo
Funcion 		Vendedores.1
'''
@login_required(login_url='/logearse')
def formularioProducto(request):
	categorias = CategoriaProducto.objects.all()
	subcategorias = CategoriaInterna.objects.all()
	tipoIVA = TipoIVA.objects.all()
	empresas = Empresa.objects.all()
	return render_to_response('Agregar_producto.html',locals(), context_instance=RequestContext(request))		

@login_required(login_url='/logearse')
def formularioCategoria(request):
	categorias = CategoriaProducto.objects.all()
	return render_to_response('Agregar_subcategoria.html',locals(), context_instance=RequestContext(request))

@login_required(login_url='/logearse')
def agregarProducto(request):
	nombreProducto = request.POST['nombre_producto']
	presentacion = request.POST['presentacion']
	precioCompra = request.POST['precio_compra']
	precioVenta = request.POST['precio_venta']
	iva = TipoIVA.objects.get(pk=request.POST['iva'])
	descuento = request.POST['descuento']
	foto = "images/"+request.POST['foto']
	fotoUrl = settings.MEDIA_URL+request.POST['foto']
	descripcion = request.POST['descripcion']
	subcat= CategoriaInterna.objects.get(pk=request.POST['subcategoria'])
	empresa= Empresa.objects.get(pk=request.POST['empresa'])
	producto= Producto(nombre_producto=nombreProducto, descripcion=descripcion, costo=precioCompra, costo_venta=precioVenta, presentacion=presentacion, imagen=foto, descuento=descuento, empresa=empresa, iva=iva, categoria=subcat)
	producto.save()
	return HttpResponseRedirect('/inicioVendedorCatalogo/')

@login_required(login_url='/logearse')
def agregarSubcategoria(request):
	categoriaPadre = CategoriaProducto.objects.get(pk=request.POST['categoria'])
	nombreSubcategoria = request.POST['nombre_subcategoria']
	subcategoria = CategoriaInterna(nombre_cat_interna=nombreSubcategoria,cat_producto=categoriaPadre)
	subcategoria.save()
	return HttpResponseRedirect('/inicioVendedorCatalogo/')


@login_required(login_url='/logearse')
def modificarProductoformulario(request, idProducto):
	categorias = CategoriaProducto.objects.all()
	subcategorias = CategoriaInterna.objects.all()
	tipoIVA = TipoIVA.objects.all()
	empresas = Empresa.objects.all()
	producto = Producto.objects.get(pk=idProducto)
	return render_to_response('Modificar_producto.html',locals(), context_instance=RequestContext(request))

# esto esta mal, es el mismo codigo de agregar producto
@login_required(login_url='/logearse')
def modificarProducto(request):
	p = Producto.objects.get(pk=request.POST['pk'])
	p.nombre_producto = request.POST['nombre_producto']
	p.presentacion = request.POST['presentacion']
	p.costo = request.POST['precio_compra']
	p.costo_venta = request.POST['precio_venta']
	p.iva = TipoIVA.objects.get(pk=request.POST['iva'])
	p.descuento = request.POST['descuento']
	p.imagen = "images/"+request.POST['foto']
	p.descripcion = request.POST['descripcion']
	p.categoria= CategoriaInterna.objects.get(pk=request.POST['subcategoria'])
	p.empresa= Empresa.objects.get(pk=request.POST['empresa'])
	p.save()
	return HttpResponseRedirect('/inicioVendedorCatalogo/')

@login_required(login_url='/logearse')
def visualizarProducto(request,idProducto):
	producto = Producto.objects.get(pk=idProducto)
	return render_to_response('Detalle_producto.html',locals(), context_instance=RequestContext(request))	


'''
Autor 			Jhonatan Acelas Arevalo
Fecha 	 		11 Julio 2015
Descripcion  	retorna falso o verdadero si el usuario contiene los permisos sobre los rol de usuarios
Funcion 		Vendedores.1
Modifico
'''
@login_required(login_url='/logearse')
def pedidosVendedor(request):
	return request.user.groups.filter(name__in=['PV', 'AV']).exists()

@login_required(login_url='/logearse')
def catalogoVendedor(request):
	return request.user.groups.filter(name__in=['CV', 'AV']).exists()

@login_required(login_url='/logearse')
def reportesVendedor(request):
	return request.user.groups.filter(name__in=['RV', 'AV']).exists()

@login_required(login_url='/logearse')
def usuariosVendedor(request):
	return request.user.groups.filter(name__in=['UV', 'AV']).exists()
