
# coding: utf-8

# In[84]:


# Importamos las librerias que vamos a usar
import requests
from urllib.error import HTTPError
from urllib.error import URLError
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import datetime

# Definimos la funcion que busca y recupera los enlaces de las gasolineras de Barcelona
def get_comunity_links(url):
    comu_links = []
    provi_links = []
    try:
        page = requests.get(url)
    except HTTPError as e:
        print(e)
    except URLError:
        print("Server down or incorrect domain")
    else:
        res = BeautifulSoup(page.content,"html.parser")
        for link in res.find_all('a'):
            if link.has_attr('href'):
                if '/c/precio-gasoil-calefaccion-' in link.attrs['href']:
                    comu_links.append(link.attrs['href'])
                if '/p/precio-gasoil-calefaccion-' in link.attrs['href']:
                    provi_links.append(link.attrs['href'])
    return comu_links, provi_links

def get_provincia_links(comu_links,provi_links):
    for comu_link in comu_links:
        try:
            html = ("https://www.clickgasoil.com" + comu_link)
            page = requests.get(html)
        except HTTPError as e:
            print(e)
        except URLError:
            print("Server down or incorrect domain")
        else:
            #res = BeautifulSoup(open(page, 'r'),"html.parser",from_encoding="iso-8859-1")
            res = BeautifulSoup(page.content,"html.parser", from_encoding="latin1")
        for link in res.find_all('a'):
            if link.has_attr('href'):
                if '/p/precio-gasoil-calefaccion-' in link.attrs['href']:
                    provi_links.append(link.attrs['href'])
                if '/p/precio-de-gasoil-calefaccion-' in link.attrs['href']:
                    provi_links.append(link.attrs['href'])
    return provi_links

def get_city_links(provi_links):
    city_links = []
    for provi_link in provi_links:
        try:
            html = ("https://www.clickgasoil.com" + provi_link)
            page = requests.get(html)
        except HTTPError as e:
            print(e)
        except URLError:
            print("Server down or incorrect domain")
        else:
            #soup = BeautifulSoup(open(page, 'r'),"html.parser",from_encoding="iso-8859-1")
            soup = BeautifulSoup(page.content,"html.parser", from_encoding="latin1")
        for link in soup.find_all('a'):
            if link.has_attr('href'):
                if '/m/precio-gasoil-calefaccion-' in link.attrs['href']:
                    city_links.append(link.attrs['href'])
                if '/m/precio-de-gasoil-calefaccion-' in link.attrs['href']:
                    city_links.append(link.attrs['href'])
    return city_links

def get_station_links(city_links):
    station_links = []
    for i,city_link in enumerate(city_links):
        print("Llevamos: " + str(i) + "municipios de 7000")
        try:
            html = ("https://www.clickgasoil.com" + city_link)
            page = requests.get(html)
        except HTTPError as e:
            print(e)
        except URLError:
            print("Server down or incorrect domain")
        else:
            # Estructuramos el contenido de la web obtenido para ser consultado facilmente
            estacion = BeautifulSoup(page.content,"html.parser")

            #Buscamos los links:
            for link in estacion.find_all('a'):
                if link.has_attr('href'):
                    if '/g/' in link.attrs['href']:
                        station_links.append(link.attrs['href'])
    return station_links

# Definimos la funcion que busca y recupera todos los datos referente a cada gasolinera
def get_info(station):
    try:
        html = ("https://www.clickgasoil.com" + station)
        page = requests.get(html)
    except HTTPError as e:
        print(e)
    except URLError:
        print("Server down or incorrect domain")
    else:
        # Estructuramos el contenido de la web obtenido para ser consultado facilmente
        soup = BeautifulSoup(page.content,'html.parser')
        
        # Existe la gasolinera?
        #existe = soup.find ("div", {"class":"columns small-12 clearfix"})
        #word = existe.text
        #if "no existe" not in word:

        # Buscamos la información general de cada gasolinera: Marca, Direcion, Poblacion, Horario
        info_gasolinera = soup.find("div", {"class":"column small-4 datos_gasolinera"})
        
        if(info_gasolinera):
            print("Existe")
            # Buscamos ahora las etiquetas div que hemos detectado, son las que engloban la información que buscamos
            div_lista = info_gasolinera.find_all('div')

            # Recorremos la información y guardamos los datos que nos interesan
            for i,dato in enumerate(div_lista):
                temp = dato.text.split(":")
                if (i==0): 
                    marca = temp[1]
                if (i==1):
                    direccion = temp[1]
                if (i==2):
                    poblacion = temp[1]
                if (i==3):
                    horario = temp[1] + temp[2]

            # Buscamos la tabla que contiene los precios de los combustibles a fecha de la consulta
            table = soup.find("table", { "class" : "small-12" })

            # Buscamos todas las filas de esta tabla y las guardamos en una lista
            td_list = table.find_all('td')

            # Recorremos la información y guardamos los datos que nos interesan
            for i,element in enumerate(td_list):
                if(i == 1):
                    precio_gasoil = td_list[1].text[:-1]
                    gasoil = precio_gasoil
                if (i == 7):
                    precio_gas95 = td_list[7].text[:-1]
                    gas95 = precio_gas95
                if (i == 9):
                    precio_gas98 = td_list[9].text[:-1]
                    gas98 = precio_gas98
            # Guardamos la fecha de la consulta
            fecha = datetime.datetime.now()

            # Devolvemos los datos
            return marca,gasoil,gas95,gas98,direccion,poblacion,horario,fecha
        else:
            return (0,0,0,0,0,0,0,0)

# Para cada estacion, vamos a su pagina donde obtenemos todos sus datos y los precios del combustible del dia
def precios_gasolineras(station_links):
    for i,station in enumerate(station_links):
        print("Llevamos " + str(i) + "municipios de 10078")
        marca,gasoil,gas95,gas98,direccion,poblacion,horario,fecha = get_info(station)
        
        if(poblacion != 0):
        
            # Guardamos los datos en listas que nos permitiran luego crear un dataframe que exportaremos.
            marcas.append(marca)
            gasoils.append(gasoil)
            gas95s.append(gas95)
            gas98s.append(gas98)
            direcciones.append(direccion)
            poblaciones.append(poblacion)
            horarios.append(horario)
            fechas.append(fecha)
            urls.append(station)

    # Creamos un dataframe con todos los datos obtenidos
    print ("Creamos el dataframe Final")
    df = pd.DataFrame(
        {'Marca':marcas,
         'Gasolina 95':gas95s,
         'Gasolina 98':gas98s,
         'Gasóleo A':gasoils,
         'Direccion':direcciones,
         'Poblacion':poblaciones,
         'Horario':horarios,
         'Fecha': fechas,})
    return df

# Parseando la web ClickGasoil que nos ofrece los precios de Gasóleo A, Gasolina 95 y Gasolina 98 de cada gasolinera de España
# Crear listas para guardar los datos
# Comprobamos si esta el archivo con las direcciones de las estaciones a consultar:
csv_estaciones_anterior = 0
try:
    df_stations = pd.read_csv("estaciones_servicio.csv")
except OSError as e:
    #print(e)
    csv_estaciones_anterior = 1 # No se ha conseguido leer
else:
    csv_estaciones_anterior = 0 # No hay error de lectura

if (csv_estaciones_anterior == 1):
    url = "https://www.clickgasoil.com/c/precio-gasoil-calefaccion"
    comu_links, provi_links = get_comunity_links(url)
    print ("Ya tenemos las comunidades, son:" + " " + str(len(comu_links + provi_links)))

    provi_links = get_provincia_links(comu_links,provi_links)
    print ("Ya tenemos las provincias, son:" + " " + str(len(provi_links)))

    bcn_provincia = ""
    for station in provi_links:
        if "barcelona" in station:
            bcn_provincia = station

    city_links = get_city_links(provi_links)
    print ("Ya tenemos las ciudades, son:" + " " + str(len(city_links)))
    station_links = get_station_links(city_links)
    print ("Ya tenemos las estaciones de servicio! y son: " + " " + str(len(station_links)))
    df_estaciones = pd.DataFrame({'Estaciones':station_links})
    df_estaciones.to_csv("estaciones_servicio.csv", sep=',')
else:
    print("Estaciones cargando...")
    station_links = df_stations["Estaciones"].tolist()
    
# Comprobamos si hay archivo csv con datos existentes:
csv_precios_anterior = 0
try:
    df2 = pd.read_csv("Precio_combustible_spain.csv")
except OSError as e:
    #print(e)
    csv_precios_anterior = 1 # No se ha conseguido leer
else:
    csv_precios_anterior = 0 # No hay error de lectura

if (csv_precios_anterior == 1):
    # Crear listas para guardar los datos
    marcas = []
    gas95s = []
    gas98s = []
    gasoils = []
    direcciones = []
    poblaciones = []
    horarios = []
    
else:
    print("Precios cargando...")
    marcas = df2["Marca"].tolist()
    gas95s = df2["Gasolina 95"].tolist()
    gas98s = df2["Gasolina 98"].tolist()
    gasoils = df2["Gasóleo A"].tolist()
    direcciones = df2["Direccion"].tolist()
    poblaciones = df2["Poblacion"].tolist()
    horarios = df2["Horario"].tolist()
    fechas = df2["Fecha"].tolist()

# Capturamos los datos y creamos un dataframe con ellos.
df = precios_gasolineras(station_links) 

# Exportamos los datos en un archivos csv
df.to_csv("Precio_combustible_Spain.csv", sep=',')

