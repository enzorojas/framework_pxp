#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Instalador del Framework PXP Kplian 
# Author Freddy Rojas
#Version 1.0
# (c)2013 Kplian Ltda.

import os
import sys
import subprocess
import glob
import urllib2
import re
import time
from cStringIO import StringIO
import getpass
import threading
import time
from datetime import datetime

#from msilib.schema import SelfReg

#Clase para el manejo de colores de mensaje
class bcolors:
    #HEADER = '\033[95m'
    HEADER = '\033[1;36m'
    #OKBLUE = '\033[94m'
    OKBLUE = '\033[1;34m'
    OKGREEN = '\033[92m'
    KPLIAN = '\033[1;33m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'    

class Progress(object):
    def __init__(self):
        self._seen = 0.0

    def update(self, total, size, name):
        self._seen += size
        pct = (self._seen / total) * 100.0
        print '%s progress: %.2f' % (name, pct)

class file_with_callback(file):
    def __init__(self, path, mode, callback, *args):
        file.__init__(self, path, mode)
        self.seek(0, os.SEEK_END)
        self._total = self.tell()
        self.seek(0)
        self._callback = callback
        self._args = args

    def __len__(self):
        return self._total

    def read(self, size):
        data = file.read(self, size)
        self._callback(self._total, len(data), *self._args)
        return data
    
print '\r'
print  '**************************************************************************\r'
print  bcolors.KPLIAN + '* ----------------   Instalador Framework PXP Kplian   ----------------  *\r' + bcolors.ENDC
print  '*                                                                        *\r'
print  '* Version 1.0                                                            *\r'
print  '* Author Freddy Rojas                                                    *\r'
print  '* (c)2013 Kplian Ltda.                                                   *\r'
print  '**************************************************************************\n'


if (os.getenv('USER') != 'root'):
    sys.exit('>>>ERROR: Instalacion detenida.\nDebe estar logueado con el usuario \'root\'.\n')

print "Iniciando Script de instalacion...."
time.sleep(3)

#### Definicion de clases
        
"Clase para la verificacion de sistema operativo/aplicaciones, version y arquitectura"
class AnalizarDistro:
    OS = None
    ARCH = None
    VESION = None
    pARCH = None
    PACKMANAGER = None
    oSName = None
    oSFamily = None
    pathCmd = None
    PID = None #Process ID del proceso en ejecucion
    testMode = None
    #def __init__(self):
    
    #Imprimir 'msg' en color Rojo"              
    def prinxi(self, msg):
        exit (bcolors.FAIL + '\n>>>' + msg + bcolors.ENDC)
        
    #Imprimir 'msg' en color Amarillo en la salida estandar de la consola"              
    def prinout(self, msg):
        if not msg:
            msg = ""
        else:
            msg = '\n' + msg;
        
        print (bcolors.WARNING + msg + bcolors.ENDC)
    
    #Imprimir 'msg' en color Rojo"              
    def prinx(self, msg):
        exit (bcolors.FAIL + '\n>>>ERROR:\n' + msg + bcolors.ENDC)
    
    #Imprimir 'msg' en color Verde"    
    def prinok (self, msg):
        print (bcolors.OKGREEN + '\n>>>' + msg + bcolors.ENDC)
    
    #Imprimir 'msg' en color Amarillo"
    def prinw(self, msg):
        print (bcolors.WARNING + '\n>>>' + msg + bcolors.ENDC)
    
    #Imprimir 'msg' en color Lila"
    def prini(self, msg):
        print (bcolors.HEADER + '\n>>>' + msg + bcolors.ENDC)
        
    #Imprimir 'msg' en color Azul" para comandos
    def princmd(self, msg):
        print (bcolors.OKBLUE + '\r>>>Ejecutando comando: ' + msg + bcolors.ENDC + "\r")
    
    def readInput(self, msg):
        try:
            return raw_input("\nResponda por favor, "+bcolors.HEADER + msg +  bcolors.ENDC)
        except:
            pass
    def readPassword(self, msg):
        try:
            self.prini("Ingrese la contraseña: ")
            return getpass.getpass()
        except:
            pass
        
    #Funcion que desplega un menu para la instalacion de solo Framework PXP sin dependencias    
    def menuNotSupported(self, msg):
        self.executeGet("cls")
        self.prinw(msg)
        
        self.prinw("La instalacion automatica de paquetes necesarios como Apache + PHP 5.2.x o 5.3.x y Postgresql 9.1.x \n"
                   "Instale manualmente estos paquetes y a continuaion elija instalar el framewok PXP.")
        self.prini("==================== MENU ====================")
        self.prini("Desear instalar el framerwork PXP sin PostgreSQL, Apache y PHP? (escriba si o no)")        
        opcion = self.readInput('si/no? [si]: ')
        if (opcion == 'si' or opcion == '') :
            self.prini("Iniciando modo de instalacion de solo Framework PXP........\n"
                       "(Esta modo no instala los paquetes requeridos de PostgreSQL, Apache y PHP.\nSe asume que estos ya existen o que seran instalados manualmente)")
            time.sleep(3)
            #XXXXXXXXXXXXXXXXX poner funcion de instalacion PXP Only
            
        else:
            self.prinxi("Ha abandonado la instalacion de PXP Kplian")           
        
    #Busca informacion (nombre, version, arquitectura) del Sistema operativo"       
    def detectOS(self):  
        filelist = glob.glob('/etc/*-release')
        if filelist:            
            self.OS = self.executeExit("awk '/DISTRIB_ID=/' /etc/*-release | sed 's/DISTRIB_ID=//' | tr '[:upper:]' '[:lower:]'")                            
            self.ARCH = self.executeExit("uname -m | sed 's/x86_//;s/i[3-6]86/32/'");
            self.VERSION = self.executeExit("awk '/DISTRIB_RELEASE=/' /etc/*-release | sed 's/DISTRIB_RELEASE=//' | sed 's/[.]0/./'");
            if not self.OS:
                self.OS = self.executeExit("awk 'NR==1{print $1}' /etc/*-release")
            if not self.VERSION:
                self.VERSION = self.executeExit("awk 'NR==1{print $3}' /etc/*-release")
        else:
            filelist = glob.glob('/etc/*-version')
            if not filelist:
                self.prinx("Distribucion Linux no soportada")
                
            self.OS = self.executeExit("awk '/DISTRIB_ID=/' /etc/*-release | sed 's/DISTRIB_ID=//' | tr '[:upper:]' '[:lower:]'")                            
            self.ARCH = self.executeExit("uname -m | sed 's/x86_//;s/i[3-6]86/32/'");
            self.VERSION = self.executeExit("awk '/DISTRIB_RELEASE=/' /etc/*-release | sed 's/DISTRIB_RELEASE=//' | sed 's/[.]0/./'");
            
            if not self.OS:
                self.OS = self.executeExit("awk 'NR==1{print $1}' /etc/*-version")
            if not self.VERSION:
                self.VERSION = self.executeExit("awk 'NR==1{print $3}' /etc/*-version")
        
        if self.ARCH.find('64') != -1:
            self.pARCH = "x86_64"
        else:
            self.pARCH = "i386"
                     
        self.OS = self.OS.strip(' \t\n\r')
        self.VERSION = self.VERSION.strip(' \t\n\r')
        self.ARCH = self.ARCH.strip(' \t\n\r')
        
        self.detectOSVersion()
        self.prini("Distribucion Linux detectada: %s %s de %s bits (%s) " % (self.OS, self.VERSION, self.ARCH, self.pARCH))
    
    #Funcion para identificar la version del Sistema Operativo y validar las versiones soportadas
    def detectOSVersion(self):
        self.repoSource = ""        
        self.oSSerie = ''.join(re.findall(r'^(.+?)\.', self.VERSION))  #Se extrae y guarda el  digito correspondiente a la version mayor
        self.oSName = self.OS.lower()  #Guardar el nombre de la distribucion en miniscula
        
        if not self.oSSerie: #En caso de que no se tengan versines menores el OSSerie sera igual a la VERSION
            self.oSSerie = self.VERSION
               
        #Verificar si es una distribucion de la familia RedHat 
        if glob.glob('/etc/redhat-release'):
            self.oSFamily = 'redhat'
            self.PACKMANAGER = 'rpm'
            #Configurar los repositorios para CentOS/RedHat
            if self.oSName == "centos" or self.oSName == "redhat":                
                 
                if self.oSSerie < "5":
                    self.prinx(self.OS +" "+self.VERSION +' No esta soportado, la version minima es CentOS 5.5.')                 
                                    
            #Configurar los repositorios para Fedora        
            elif self.oSName == "fedora":
                
                if self.oSSerie  < 12:
                    self.prinx('Fedora' + self.VERSION + 'No esta soportado, la version minima es Fedora 12')                    
                    
        #Verificar si es una distribucion de la familia SuSE        
        elif glob.glob('/etc/SuSE-release'):
            self.oSFamily = 'suse'
            self.PACKMANAGER = 'rpm'
            self.menuNotSupported(self.OS + ' aun no esta soportado, visite www.kplian.com para mantenerse informado de las actualizaciones.')
            
        #Verificar si es una distribucion de la familia Debian
        elif glob.glob('/etc/debian_version'):
            self.oSFamily = 'debian'
            self.PACKMANAGER = 'dpkg'
            self.menuNotSupported(self.OS + ' aun no esta soportado, visite www.kplian.com para mantenerse informado de las actualizaciones.')
            
        #Otra distribucion distinta de las anteriores
        else:
            self.menuNotSupported('Instalacion detenida. Distribucion no soportada')
            
    #Funcion para validar le pre-existencias de paquetes, comando u archivos especificos        
    def validatePrerequisites(self):
        if (not self.packageExist("git")):
            self.prinx("El paquete basico Git no se encuentra instalado en el sistema. La instalaciona\n"
                       "ha sido detenida, antes de instalar PXP por favor instale Git: Yum install git")
            
        elif (not self.packageExist("wget")):
              self.prinx("El paquete basico Wget no se encuentra instalado en el sistema. La instalaciona\n"
                       "ha sido detenida, antes de instalar PXP por favor instale Wget: yum install wget")            
    
    #Funcion que devuelve el archivo de configuración correspondiente al paquete 'package'
    def getConfigFile(self, package):
        configFile= None
        #Deternimar el archivo de configuracion del paquete package                  
        if package == "php":
            configFile = self.executeGet("find /etc/ -maxdepth 1|grep -e '/php\.ini$'")
            if not configFile:
                self.prinx("No se ha encontrado el archivo de configuracion de: "+package+".ini, intente configurar el archivo manualmente.")
                                
        elif package == "postgresql" or "pg_hba":
            #Obtenr la ruta absoluta del archivo de servico Postgres
            pathService = self.executeGet("find /etc/init.d/ -maxdepth 1|grep -i 'postgres'|awk NR==1").strip(" \n\r")
            if not pathService:
                pathService = self.executeGet("find /etc/init.d/ -maxdepth 1|grep -i 'ppas-9'|awk NR==1").strip(" \n\r")
            if pathService:                
                if pathService.find('postgres') != -1:
                    #Obtener la ruta al archivo de configuración de postgresql.conf                    
                    configFile = ''.join(re.findall(r'PGDATA=(.*?)$',
                                                    self.executeGet(" cat "+pathService+"|grep -i 'pgdata='|awk NR==1")))
                    if package == "postgresql":
                        configFile = configFile + "/postgresql.conf"
                    elif package == "pg_hba":
                        configFile = configFile + "/pg_hba.conf"
                    
                elif pathService.find('ppas') != -1:
                    #Obtener la ruta al archivo de configuración de postgresql.conf                    
                    configFile = ''.join(re.findall(r'PGDATA=(.*?)$',
                                                    self.executeGet(" cat "+pathService+"|grep '/data/'|awk NR==1")))
                    if package == "postgresql":
                        configFile = configFile + "data/postgresql.conf"
                    elif package == "pg_hba":
                        configFile = configFile + "data/pg_hba.conf"
            else:
                self.prinx("No se ha encontrado el archivo de configuracion de: "+package+".conf, intente configurar el archivo manualmente.")                
            
        elif package == "httpd":
            #Obtenr la ruta absoluta del archivo de servico Apache
            pathService = self.executeGet("find /etc/init.d/ -maxdepth 1|grep -i 'http'|awk NR==1").strip(" \n\r")           
            if not pathService:
                pathService = self.executeGet("find /etc/init.d/ -maxdepth 1|grep -i 'apache'|awk NR==1").strip(" \n\r")
            if pathService:
                #Obtener la ruta al archivo de configuración de httpd.conf                
                configFile = ''.join(re.findall(r'config: (.*?)$',
                                                    self.executeGet(" cat "+pathService+"|grep -e 'config:.*httpd.conf'")))
                configFile = configFile + ""
            else:
                self.prinx("No se ha encontrado el archivo de configuracion "+package+".conf, intente configurar el archivo manualmente.") 
            
        else:
            #configFile = self.executeGet("rpm -q --configfiles "+package+"|grep '"+package+"\.conf'")
            self.prinx("Error de ejecución de comandos: paquete "+package+" no definido para autoconfiguracion")        
                
        if configFile:
            self.prini("Archivo de configuracion detectado: "+configFile+"\n")
            
        else:
            self.prinx("No se ha encontrado el archivo de configuracion de: "+package+", intente configurar el archivo manualmente.")
        
        if configFile == "":
            configFile = None
        #Quitar los espacios, retornos de carro que estan por demas en la cadega configFile
        if not configFile:
            configFile = configFile.strip(" \n\r")
        
        return configFile
    
    #Función para modificar archivos de configuración. Este recibe el nombre del
    #archivo de configuracion o la ruta absoluta del archivo de configuracion 
    def setConfigValue(self, configFile, key, value):        
        commentChar = "#"               
        #Verificar si la linea 'clave' esta comentada en el archivo de configuracion        
        configLine = self.executeGet("cat "+configFile+"|grep -i "+key)
        #isCommented = configLine.|strip(" ").startswith(";")
        
        #Extraer la ruta absoluta al archivo de configuracion de la cadena configFile
        path = ''.join(re.findall(r'^(.*)\/', configFile))+"/"
        #Extraer solo el nombre de la cadena configFile, luego añadir etiquetas al nombre
        nameBK = ''.join(re.findall(r''+path+'(.+?)$', configFile))+".backup_$(date +%d-%m-%Y--%H-%M)"
        
        #Hacer una copia de seguridad del archivo de configuracion
        self.executeVerbose("cp "+configFile+" "+path+nameBK)
        
        if (configFile.find('php') != -1):            
            commentChar = ";"
        #Imprimir la clave que se modificara
        self.prini("Estableciendo la clave: "+key+" = "+value+" (en archivo: "+configFile+")")
        
        #Verificar si la linea que concide con la cave 'key' existe y esta descomentada
        if not self.executeGet("grep -E \"(([^"+commentChar+"]|^)"+key+".*)=(.*)$\" "+configFile):
            #Obtener el numero de linea de la untima coincidencia del patron pattern
            lineNumber = self.executeGet("nl -b a "+configFile+"|grep -E \"(([^"+commentChar+"]|^)"+
                                         key+".*)=(.*)$\" |"+"awk '{print $1}'|sort -r|awk NR==1")
            if lineNumber:
                lineNumber = str(int(lineNumber.strip(" \n\r"))+1)
            #Insertar una nueva linea con los valores pattern y value a continuacion de la ultima coicidencia 
            #con el patron pattern
            self.executeVerbose("sed -i '"+lineNumber+"i"+key+"= "+value+"' "+configFile)
        else:       
            #Comentar la linea correspondiente a la clave 'key' y añadir una linea con la clave 'key'
            #y su nuevo valor 
            #XXXXXXXXXXXXXXX modificar a silent
            self.executeVerbose("sed -i -r -e \"s/(([^"+commentChar+"]|^)"+key+".*)=(.*)$/"+commentChar+key+
                                "=\\3  "+commentChar+"Comented $(date +%d-%m-%Y--%H:%M) by PXP Installer \\n"+
                                key+" = "+value+"/\" "+ configFile)
    
    #Reemplaza la porcion de texto que sucede a la cadena 'pattern' en la linea que coincide 
    #con patron pattern, con el valor value    
    def setConfigLine(self, configFile, pattern, value):
        commentChar = "#"
        if (configFile.find('xxxxx') != -1):            
            commentChar = ";"
        
        #Imprimir la linea pattern que se modificara
        lineText = pattern.replace(".*", "    ")
        self.prini("Modificando la linea: "+lineText+" (en archivo: "+configFile+")")
        #Verificar si la linea que concide con pattern existe y  esta descomentada
        if not self.executeGet("grep -E \"(([^"+commentChar+"]|^)"+pattern+").*(.*)$\" "+configFile):
            #Obtener el numero de linea de la untima coincidencia del patron pattern
            lineNumber = self.executeGet("nl -b a "+configFile+"|grep -E \"("+pattern+").*(.*)$\" |"+
                                         "awk '{print $1}'|sort -r|awk NR==1")
            if lineNumber:
                lineNumber = str(int(lineNumber.strip(" \n\r"))+1)
            #Insertar una nueva linea con los valores pattern y value a continuacion de la ultima coicidencia 
            #con el patron pattern
            self.executeVerbose("sed -i '"+lineNumber+"i"+lineText+"\\t\\t"+value+"' "+configFile)
        else:
            self.executeVerbose("sed -i -r -e \"s/(([^"+commentChar+"]|^)"+pattern+
                                ").*(.*)$/#\\0  #Comented $(date +%d-%m-%Y--%H:%M) by PXP Installer \\n"+
                                "\\1\\t\\t"+value+"/\" "+ configFile)                
            
        
    def configureFiles(self):
        self.executeGet("updatedb")
        
        #####Configuracion de archivos  de PHP
        phpFile = self.getConfigFile("php")
        
        if self.testMode: phpFile = "./php.ini"
        self.prini("CONFIGURACION Y PREPARACION DEL SERVIDOR WEB: APACHE + PHP\n")
        #deshabilitar errores por defecto
        self.setConfigValue(phpFile, "display_errors", "Off")
        #configurarciond e persistnecia en php postgres (esto es opcional depende si queremos
        #conexiones persistentes solo experimental)
        self.setConfigValue(phpFile, "pgsql.allow_persistent", "On")
        self.setConfigValue(phpFile, "pgsql.auto_reset_persistent", "On")
        #tiempo de ejecución 30 minutos considerando sistemas complejos, No es lo mismo que una página web comun
        self.setConfigValue(phpFile, "max_execution_time", "1800")
        #Manejo de archivos para subir la capacidad de envio
        self.setConfigValue(phpFile, "memory_limit", "256M")
        self.setConfigValue(phpFile, "post_max_size", "500M")
        self.setConfigValue(phpFile, "upload_max_filesize", "500M")
        #Prueba para verficar si HP esta corriendo con apache
        '''self.executeGet("echo \"<?php echo phpinfo(); ?>\" > /var/www/html/test.php")
        self.executeGet("curl http://127.0.0.1/test.php")'''        
        
        #####Configuracion de archivos de Postgresql
        postgresqlFile = self.getConfigFile("postgresql")
        
        if self.testMode:postgresqlFile = "./postgresql.conf"
        self.prini("CONFIGURACION Y PREPARACION DE LA BASE DE DATOS\n")
        #self.setConfigValue(postgresqlFile, "", )
        
        pg_hbaFile = self.getConfigFile("pg_hba")
        
        if self.testMode: pg_hbaFile = "./pg_hba.conf"
        self.setConfigLine(pg_hbaFile, "local.*all.*all", "md5")
        self.setConfigLine(pg_hbaFile, "host.*all.*all", "md5")
        
        ####Configuracion de archivos de Apache        
        httpdFile = self.getConfigFile("httpd")
        httpdFile = "./httpd.conf"
        
        
                    
    
    #Ejecuta comandos linux y finaliza la instalacion en caso de que ocurra un error durante la ejecucion del comando"    
    def executeExit (self, command):
        self.princmd(command)
        p = subprocess.Popen(command, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()        
        
        if err:
            if (err.lower().find('warning') != -1) or (err.lower().find('advertencia') != -1) or (err.lower().find('is already ') != -1) or (err.lower().find(' instalado ') != -1):
                self.prinw("Advertencia: "+ err)
                
            else: #(err.lower().find('error') != -1) or (err.lower().find('fatal') != -1):
                self.prinx(err)
            
        return output 
                       
        '''
        if (err):
            self.prinx(err)        
        return output'''
   
    #Ejecuta comandos linux y  devuelve el resultado de la ejecucion"
    def executeGet (self, command):
       self.princmd(command)
       p = subprocess.Popen(command, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
       (output, err) = p.communicate()
       
       if err:
           if ((err.lower().find('warning') != -1) or (err.lower().find('advertencia') != -1) 
               or (err.lower().find('is already ') != -1) or (err.lower().find(' instalado ') != -1)):
               self.prinw("Advertencia: "+ err)           
                   
           else:
               pass
       if output == "":
           output = None
       return output 
   
   #Ejecuta comandos linux y  devuelve el resultado de la ejecucion y no muestra en el OUTPUT
    def executeSilent (self, command):       
       p = subprocess.Popen(command, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
       (output, err) = p.communicate()
       
       if err:
           if ((err.lower().find('warning') != -1) or (err.lower().find('advertencia') != -1) 
               or (err.lower().find('is already ') != -1) or (err.lower().find(' instalado ') != -1)):
               self.prinw("Advertencia: "+ err)           
                   
           else:
               pass
       if output == "":
           output = None
       self.prinout(output)        
    
       return output   
    
    
    #Busca el servico en base al patron 'command' e inicializa el servico con los parametros especificados
    def executeService (self, command, params = None):
        pathService = None
        #Buscar el nombre exacto del sericio que se quiere iniciar
        if command == "postgresql":
            pathService = self.executeGet("find /etc/init.d/ -maxdepth 1|grep -i 'postgres'|awk NR==1")            
            if not pathService or pathService == "":
                pathService = self.executeGet("find /etc/init.d/ -maxdepth 1|grep -i 'ppas-9'|awk NR==1")
                
        elif command == "apache":
            pathService = self.executeGet("find /etc/init.d/ -maxdepth 1|grep -i 'http'|awk NR==1")            
            if not pathService or pathService == "":
                pathService = self.executeGet("find /etc/init.d/ -maxdepth 1|grep -i 'apache'|awk NR==1")
        else:
            pathService = self.executeGet("find /etc/init.d/ -maxdepth 1|grep -i '"+command+"'|awk NR==1")
        
        #Iniciar el servicio                
        if pathService != "" and pathService != None:
            pathService = pathService.strip(" \n\r")
            serviceName = ''.join(re.findall(r'\/etc\/init.d\/(.+?)$', pathService))            
            servidorCorriendo = self.executeGet(pathService+" status|grep -i 'pid '")
            
            if not servidorCorriendo:                                    
                if params:
                     self.executeVerbose(pathService+" "+params)
                else:
                     self.executeVerbose(pathService+" start")                                                      
            else:
                if params:
                    self.prini("El servicio de "+serviceName+" ya se esta ejecutando ("+serviceName+" "+params+"): "+servidorCorriendo)
                else:
                    self.prini("El servicio de "+serviceName+" ya se esta ejecutando ("+serviceName+"): "+servidorCorriendo)
            
            self.prini("Configurando el servicio "+serviceName+" para que arranque automaticamente al inicio del Sistema Operativo.")                
            self.executeGet("chkconfig "+serviceName+" on")
        else:
            self.prini("Servicio no encontrado para el comando: "+command)            
    
    #Funcion que habilita las conexiones de red y configura SELinux para apache y postgresql
    def enableNetConnections(self, params = None):
        self.executeGet("setsebool -P httpd_can_network_connect_db=1")
        self.prini("Desea que el instalador habilite automaticamente los puertos 80, 443 (http, https) y 5432 (postgresql)?")
        opcion = self.readInput('si/no? [si]: ')
               
        if opcion == "si" or opcion == "":
            self.prini("Abriendo los puertos 80, 443 y 5432 con iptables...")                     
            self.executeGet("iptables -I INPUT -p tcp --dport 80 -j ACCEPT")
            self.executeGet("iptables -I INPUT -p tcp --dport 443 -j ACCEPT")
            self.executeGet("iptables -I INPUT -p tcp --dport 5432 -j ACCEPT")        
            self.executeGet("/etc/init.d/iptables save")
        else:
            self.prinw("Se ha cancelado la autoconfiguracion de puertos...")
                    
    #Ejecuta comandos linux y  muestra el resultado de la ejecucion en tiempo real"
    def executeVerbose (self, command):        
        self.princmd(command)
        try:
            p = subprocess.Popen(command + " 2>&1 & echo pid=$!", stdout=subprocess.PIPE,stderr=subprocess.STDOUT, shell=True)
        except:
            pass
                         
        error = None
        requires = None
        multilib = None
        errorcode = p.returncode# Captura del codigo de error, 0 --> no hay error,  1 --> Operation not permitted, 5 --> I/O error, etc
        #Procesar la salida del comando, tanot el STDOUT y STDERR para mostrarselas al usuario
        #y analizar los posibles errores
        while True:
            #out = p.stdout.read(1)#Leer el stdout letra por letra          
            out = p.stdout.readline()#Leer el stdout linea por linea
            
            if out == '' and p.poll() != None:                
                break
            
            if out != '':                
                sys.stdout.write(out)
                sys.stdout.flush()
                                   
            #Verificar si existe algun mensaje de error y/o requerimiento de alguna dependencia
            #para intentar resolverla automaticamente
            line = out.rstrip()
            if(line.lower().find('pid=') != -1):                
                self.PID = ''.join(re.findall(r'pid=(.+?)$', line))                
                
            if(line.lower().find('downloading packages:') != -1):                
                self.prini("Descargando paquetes, espere por favor.....")
                 
            if ((line.lower().find('error: protected') != -1) or (line.lower().find('protected multilib') != -1)):
                multilib = line
                break
            
            elif ((line.lower().find('error: ') != -1) or (line.lower().find('error') != -1)):
                error = line
                
            if ((line.lower().find('error:') != -1) or (line.lower().find('error') != -1)):
                error = line
            
            elif ((line.lower().find('requires') != -1) or (line.lower().find('requiere') != -1) or
                  (line.lower().find('necesita ') != -1) ) and error:
                requires = line
                break
                        
        '''
        Error de cancelacion a media instalacion: CRITICAL:yum.main
        cd /var/lib/rpm
        rm __db*
        rpm --rebuilddb'''    
                              
        #Si se encontra un mensaje de error y requerimeinto de dependencia, 
        #intentar instalar la dependencia o desinstalar e instalar de nuevo la dependecia.
        if(error and requires):
            self.prinxi(error+"\n"+requires)            
            paqueteRequerido = ''.join(re.findall(r': (.*?)\(', requires))#Se extrae el nombre del paquete
            nombrePaquete = self.executeGet("rpm -qa |grep -i "+paqueteRequerido+" |awk NR==1 ")          
            
            if(nombrePaquete):                
                nombrePaquete = nombrePaquete.strip("\n")
                self.prini("Desea intentar desinstalar el paquete '+nombrePaquete+' y volver a instalarlo?")
                opcion = self.readInput('si/no? [si]: ')
                if opcion == "si" or opcion == "":                     
                    self.executeVerbose("yum -y remove "+nombrePaquete)
                    self.executeVerbose(command)
                else:
                    self.prinw("Se esta continuando con la instalacion omitiendo los errores de dependencias requeridas...")
                                    
            else:
                self.prini("El paquete "+paqueteRequerido+" no esta instalado.")
                self.prini("Desea intentar desinstalar el paquete "+nombrePaquete+
                           " e instalar el paquete reuerido: "+paqueteRequerido+"?")
                opcion = self.readInput('si/no? [si]: ')
                if opcion == "si" or opcion == "":                    
                    self.executeVerbose("yum -y install "+  paqueteRequerido)
                    self.executeVerbose(command)
                else:
                    self.prinw("Se esta continuando con la instalacion omitiendo los errores de dependencias requeridas...")
                
        elif(multilib):
            self.prinxi(multilib)
            self.executeVerbose("rpm -Va --nofiles --nodigest")
            oldLib = ''.join(re.findall(r'= (.*)', multilib))
            newLib = ''.join(re.findall(r's: (.*?) !', multilib))
            
            print ("LLL"+ oldLib  + "---"+newLib)
            #nombrePaquete = self.executeGet("rpm -qa |grep -i "+paqueteRequerido+" |awk NR==1 ")
            self.prini("Se ha intentado instalar la libreria  "+oldLib+" y esta esta en conflicto con: "+newLib+
                                    ". Desea remover la libreria "+oldLib+" e instala la nueva:"+newLib+"?")
            opcion = self.readInput("si/no? [si]: ")
            if opcion == "si" or opcion == "":                    
                self.executeVerbose("yum -y remove "+  oldLib)                
                self.executeVerbose(command)
            else:
                self.prinw("Se esta continuando con la instalacion omitiendo los errores de incopatibilidad de librerias...")
            #self.prinx("fin")                          
        
            
    #Verificar si el paquete existe en base al packageID (comando representativo del paquete) y su version. 
    #Ejecutar el comando de instalacion installCMD para el paqueteBase y para sus addons si existen 
    def install(self, packageID, installCmd, packageBase, packageAddons=None):        
        packageVersion = self.packageInstalled(packageID)
        
        if packageVersion:
            #Quitar espacion multiples (mas de un espacio), 
            packageVersion = packageVersion.strip(' \t\n\r')        
            packageVersion = re.sub(' +',' ',packageVersion.replace('\n', ' '))
        else: 
            packageVersion = None
        
        packageID = packageID.replace('apachectl', 'Apache')
        packageID = packageID.replace('psql', 'PostgreSQL')
        
        #Si el paquete packageID esta instalado, validar si la version del paquete es la recomendable para PXP
        if packageVersion:
            #PostgreSQL 
            if packageID == "PostgreSQL":
                if packageVersion >= "9.2":
                    #Extraer el nombre del directorio raiz
                    directory = ''.join(re.findall(r'^(.+?)\/', self.pathCmd))
                    self.prinw(("Se ha detectado "+ packageID + " version " + packageVersion +
                                " dentro el directorio: "+ directory +
                                "\nLa version recomendada por Kplian es: PostgreSQL es 9.1.x."))
                    
                    if directory != "/var":
                        self.prini("Se intentara instalar PostgreSQL en el directorio estandar: /var")
                        self.prini("Desea instalar PostgreSQL en /var?")
                        opcion = self.readInput("si/no? [si]: ")
                        if (opcion == 'si' or opcion == "") :
                            self.prini("Iniciando instalacion.....")
                            self.executeVerbose(installCmd+ " "+packageBase)
                            if packageAddons: self.executeVerbose(installCmd+ " "+packageAddons)
                        else:
                            self.prini("Instalacion de postgreSQL cancelada")
                elif packageVersion < "9":
                    self.prinw("La version recomendada por Kplian es: PostgreSQL 9.1.x. Se intentara actualizar PostgreSQL, en caso de falla intente desinstalar "+
                               packageID+" y ejecute manualmente el siguiente comando (y despues reinicie la instalacion):")
                    self.executeVerbose(installCmd+ " "+packageBase)
                    if packageAddons: self.executeVerbose(installCmd+ " "+packageAddons)
                else:
                    self.prinw("Se ha detectado "+ packageID + " version " + packageVersion + ", no hay nada que hacer, esta es una version soportada.")
            #PHP
            if packageID == "php":
                if packageVersion >= "5.4":
                    self.prinw("Se ha detectado "+ packageID + " version " + packageVersion + ". La version recomendada por Kplian es: PHP 5.3.x, intente instalar el framework en otro servidor.")
                elif packageVersion < "5":                    
                    self.prinw("La version recomendada por Kplian para la version de PHP es 5.3.x. Se intentara actualizar el paquete "+ 
                               packageID + ", en caso de falla intente desinstalar "+packageID+" y ejecute manualmente el siguiente comando (y despues reinicie la instalacion):")
                    self.executeVerbose(installCmd+ " "+packageBase)
                    if packageAddons: self.executeVerbose(installCmd+ " "+packageAddons)
                else:
                    self.prinw("Se ha detectado "+ packageID + " version " + packageVersion + ", no hay nada que hacer, esta es una version soportada.")
                                                   
        else:
            #Intentar actualizar el paquete
            self.prini("Iniciando instalacion de paquetes.....")
            self.executeVerbose(installCmd+ " "+packageBase)
            if packageAddons: self.executeVerbose(installCmd+ " "+packageAddons)
                               
        
    #Ejecuta comandos de instalacion de paquetes de repositorio y busc dinamicamente la version mas reciente"
    def installRepo (self, repoDir, command, packageStart, packageEnd):                
        ''' 
        progress = Progress()
        stream = file_with_callback(repoDir, 'rb', progress.update, repoDir)
        req = urllib2.Request(repoDir, stream)'''
        
        try:
            #Optener el listado de paquetes
            response = urllib2.urlopen(repoDir)               
            page_source = response.read()
        except urllib2.URLError:
            self.prinx("Error de conexion, el sistema no puede descagar los paquetes")
            
        #Quitar los tag Html
        p = re.compile(r'''<(?:"[^"]*"['"]*|'[^']*'['"]*|[^'">])+>''')
        page_source = p.sub('', page_source)
        
        latestVersion = max(re.findall(r''+packageStart+'(.*?)'+packageEnd,page_source))
        package = packageStart + latestVersion + packageEnd
        
        self.prini ("Instalando paquete de repositorio " + package + ".....")        
        self.executeVerbose(command+ " " + repoDir + package)        
               
        '''
        if existCurl:            
            complexCommad = """curl -L %s |sed -e :a -e 's/<[^>]*>//g;/</N;//ba' | grep -i %s | 
                               awk 'gsub(/.*%s|%s.*/,"")'|sort -nr|awk NR==1""" % (repoDir, packageStart, packageStart, packageEnd)
            
        else:
            complexCommad = """wget %s -O - |sed -e :a -e 's/<[^>]*>//g;/</N;//ba' | grep -i %s | 
                               awk 'gsub(/.*%s|%s.*/,"")'|sort -nr|awk NR==1""" % (repoDir, packageStart, packageStart, packageEnd)          
        latestVersion =  self.executeGet(complexCommad) 
        package =self.prini(packageStart + latestVersion + packageEnd)'''
    
    #Verifica si el paquete 'packageID' esta instalado en el sistema y devuleve el Path si existe,"
    #de lo contrario devulve None"
    def packageExist (self, cmdID):
        self.pathCmd = None
        if cmdID == "php":
            cmdIDm = "php -v"
        elif cmdID == "python":
            cmdIDm = "python -V"
        elif cmdID == "git":
            cmdIDm = "git --version"
        elif cmdID == "wget":
            cmdIDm = "wget --version"
        else:
            cmdIDm = cmdID
            
        output = self.executeGet(cmdIDm + " 2>&1|grep -i 'command'|grep -i ' no'")
       
        if not output:            
            self.pathCmd = self.executeGet("which " + cmdID).strip(' \t\n\r')
        else:
            self.pathCmd = self.executeGet("""locate -b '\%s'|awk NR==1""" % (cmdID))
            
            if not self.pathCmd or self.pathCmd == "":
                self.executeGet("updatedb")
                self.pathCmd = self.executeGet("""locate -b '\%s'|awk NR==1""" % (cmdID))
                
            if self.pathCmd:
                self.pathCmd = self.pathCmd.strip(' \t\n\r')
                
        return self.pathCmd   
    
    #Verifica si el paquete 'packageID' esta instalado en el sistema y devuleve la version del mismo si existe,"
    #de lo contrario devulve None"
    def packageInstalled(self, packageID):
        version = None         
        path = self.packageExist(packageID)  #Obtener la ruta al comando (incluido el comando)
        #rpm -q --info python|grep -i version|awk '{print $3}' 
               
        if path:
            #Switch para obtener la la version del paquete                 
            if packageID == 'php':
                version = self.executeGet(path + " -v 2>/dev/null|awk 'NR==1{print $2}'")
            elif packageID == 'apachectl': 
                version = self.executeGet(path + " -v 2>/dev/null|awk 'NR==1{print $3}'|sed -e 's/Apache\///'")
            elif packageID == 'psql': 
                version = self.executeGet(path + " --version 2>/dev/null|awk 'NR==1{print $3}'")
            elif packageID == 'python': 
                version = self.executeGet(path + " -V 1>/dev/null|awk 'NR==1{print $2}'")
            
            else:
                if self.PACKMANAGER == 'rpm': 
                    version = self.executeGet("rpm -q --info "+packageID+"|grep -i version|awk '{print $3}'")
                elif self.PACKMANAGER == 'dpkg': 
                    version = self.executeGet("dpkg --list "+packageID+"|grep -i version|awk '{print $3}'")                    
              
        return version
              
    #Funcion que ejecuta los comandos de instalacion de Apache + PHP"
    def installApache (self):
        self.repoSource = ""        
        #Verificar si es una distribucion de la familia RedHat 
        if glob.glob('/etc/redhat-release'):
                        
            #Configurar los repositorios para CentOS/RedHat
            if self.oSName == "centos" or self.oSName == "redhat":  
                if self.oSSerie == '6':
                    self.repoSource = ""
                    self.prinok('v.6 Instalando repositorios de dependencias para instalar Apache+PH5.3...')
                    #---->Lineas deshabilitadas provesionalmente ya que se descargaria PHP 5.4 y PXP aun no esta probado con esta version
                    # Remi Dependency on CentOS 6 and Red Hat (RHEL) 6 ##
                    #self.installRepo("http://dl.fedoraproject.org/pub/epel/6/"+self.pARCH+"/", "rpm -Uvh", "epel-", ".rpm")
                    ## CentOS 6 and Red Hat (RHEL) 6 ##
                    #self.executeVerbose("rpm -Uvh http://rpms.famillecollet.com/enterprise/remi-release-6.rpm")
                    
                elif self.oSSerie == '5':
                    self.repoSource = "--enablerepo=remi"
                    self.prinok('v.5 Instalando repositorio para instalar Apache+PHP 5.3...')
                    ## Remi Dependency on CentOS 5 and Red Hat (RHEL) 5 ##
                    self.installRepo("http://dl.fedoraproject.org/pub/epel/5/"+self.pARCH+"/", "rpm -Uvh", "epel-", ".rpm")                    
                    ## CentOS 5 and Red Hat (RHEL) 5 ## 
                    self.executeVerbose("rpm -Uvh http://rpms.famillecollet.com/enterprise/remi-release-5.rpm")
                    
                else:
                    self.prinx(self.OS+" "+self.VERSION+ " aun no soportado.")
                                    
            #Configurar los repositorios para Fedora        
            elif self.oSName == "fedora":                                
                if self.oSSerie == '16':
                    self.repoSource = ""
                    self.prinok('Instalando repositorio para instalar Apache+PHP 5.3...')
                    ## Fedora 16 ##
                    self.installRepo("http://rpms.famillecollet.com/remi-release-16.rpm", "rpm -Uvh", "remi-", ".rpm")
                    
                elif self.oSSerie == '15':
                    self.repoSource
                    ## Fedora 15 ##
                    self.installRepo("http://rpms.famillecollet.com/remi-release-15.rpm", "rpm -Uvh", "epel-", ".rpm")
                    
                elif self.oSSerie == '14':
                    self.repoSource = "--enablerepo=remi"
                    ## Fedora 14 ##
                    self.installRepo("http://rpms.famillecollet.com/remi-release-14.rpm", "rpm -Uvh", "epel-", ".rpm")
                    
                elif self.oSSerie == '13':
                    self.repoSource = "--enablerepo=remi"
                    ## Fedora 13 ##
                    self.installRepo("http://rpms.famillecollet.com/remi-release-13.rpm", "rpm -Uvh", "epel-", ".rpm")
                    
                elif self.oSSerie == '12':
                    self.repoSource = "--enablerepo=remi"
                    ## Fedora 12 ##
                    self.installRepo("http://rpms.famillecollet.com/remi-release-12.rpm", "rpm -Uvh", "epel-", ".rpm")
                else:
                    self.prinx(self.OS+" "+self.VERSION+" aun no soportado.")
                           
            #Instalacion de los paqueste de Apache + PHP
            self.prini("Instalacion de los paqueste de Apachey PHP 5.3")
            self.install("apachectl", "yum " + self.repoSource + " -y install",  " httpd")
            self.install("php", "yum " + self.repoSource + " -y install", " php php-common", 
                         " php-pecl-apc php-cli php-pear php-pdo"
                         " php-pgsql php-pecl-memcache php-pecl-memcached php53-bcmath  php53-ldap" 
                         " php-gd php-mbstring php-mcrypt php-xml")
            self.executeService("apache")            
                
                    
        #Verificar si es una distribucion de la familia SuSE        
        elif glob.glob('/etc/SuSE-release'):            
            self.menuNotSupported(self.OS + ' aun no esta soportado, visite www.kplian.com para mantenerse informado de las actualizaciones.')
            
        #Verificar si es una distribucion de la familia Debian
        elif glob.glob('/etc/debian_version'):            
            self.menuNotSupported(self.OS + ' aun no esta soportado, visite www.kplian.com para mantenerse informado de las actualizaciones.')
            
        #Otra distribucion distinta de las anteriores
        else:
            self.menuNotSupported('Instalacion detenida. Distribucion no soportada')   
        
        ####
    
    #Funcion que ejecuta los comandos de instalacion de Apache + PHP"
    def installPostgres (self):
        self.repoSource = ""        
        #Verificar si es una distribucion de la familia RedHat 
        if glob.glob('/etc/redhat-release'):
                        
            #Configurar los repositorios para CentOS/RedHat
            if self.oSName == "centos" or self.oSName == "redhat":  
                if self.oSSerie == '6' or self.oSSerie == '5':
                    self.repoSource = "--enablerepo=pgdg91"
                    self.prinok('Instalando repositorio para instalar PostgreSQL 9.1.x.....')
                    self.installRepo("http://yum.postgresql.org/9.1/redhat/rhel-"+self.oSSerie+"-"+self.pARCH+"/", "rpm -Uvh", "pgdg-"+self.oSName, ".rpm")
                                              
                else:
                    self.prinx(self.OS+" "+self.VERSION+" no esta soportado. Para mayor informacion puede escribir sus preguntas a info@kplian.com")
                                    
            #Configurar los repositorios para Fedora        
            elif self.oSName == "fedora":                                
                if self.oSSerie == '16':
                    self.repoSource = "--enablerepo=pgdg91"
                    self.prinok('Instalando repositorio para instalar PostgreSQL 9.1.x.....')
                    ## Fedora 16 ##
                    self.installRepo("http://yum.postgresql.org/9.1/fedora/fedora-"+self.oSSerie+"-"+self.pARCH+"/", "rpm -Uvh", "pgdg-"+self.oSName, ".rpm")
                    
                elif self.oSSerie >= '14':
                    self.prinw(("ADVERTENCIA: PostgreSQL 9.1.x ya no cuenta con soporte oficial para "+self.OS+" "+self.VERSION+
                               ". Se recominenda actualizar su distribución"))
                    self.prinok('Instalando repositorio para instalar PostgreSQL 9.1.x.....')
                    self.repoSource = "--enablerepo=pgdg91"
                    ## Fedora 14, 15 ##
                    self.installRepo("http://yum.postgresql.org/9.1/fedora/fedora-"+self.oSSerie+"-"+self.pARCH+"/", "rpm -Uvh", "pgdg-"+self.oSName, ".rpm")
                                        
                elif self.oSSerie < '14':
                    self.prinx(self.OS+" "+self.VERSION+" No esta soportado para la instalación de PostgreSQL 9.1.x o superior. Mayor iformación en: http://yum.postgresql.org/repopackages.php")
                else:
                    self.prinx(self.OS+" "+self.VERSION+" no esta soportado. Para mayor informacion puede escribir sus preguntas a info@kplian.com")
                           
            #Instalacion de los paquetes de Apache + PHP
            self.prini("Instalacion de los paquetes requeridos para el DBMS PostgreSQL.....")
            self.install("psql", "yum " + self.repoSource + " -y install", " postgresql91-server",
                         "postgresql91-docs postgresql91-contrib"
                         " postgresql91-plperl postgresql91-plpython postgresql91-pltcl postgresql91-test"
                         " rhdb-utils gcc-objc  postgresql91-devel postgis91")
            self.prini("Iniciando el servidor PostgresSQL...")
            self.executeService("postgresql","initdb")
            self.executeService("postgresql")
            
                  
                    
        #Verificar si es una distribucion de la familia SuSE        
        elif glob.glob('/etc/SuSE-release'):            
            self.menuNotSupported(self.OS + ' aun no esta soportado, visite www.kplian.com para mantenerse informado de las actualizaciones.')
            
        #Verificar si es una distribucion de la familia Debian
        elif glob.glob('/etc/debian_version'):            
            self.menuNotSupported(self.OS + ' aun no esta soportado, visite www.kplian.com para mantenerse informado de las actualizaciones.')
            
        #Otra distribucion distinta de las anteriores
        else:
            self.menuNotSupported('Instalacion detenida. Distribucion no soportada')   
        
        ####                                  
                        
try:
            
    distro = AnalizarDistro()   
    
    ###########################################
    showHelp = None
    if len(sys.argv) == 2:
        
        if sys.argv[1] == "test":
            distro.testMode = True
            distro.prini("Para usar este modo debe tener los archivos de configuracion php.ini,\n"
                         " postgresql.cnf, pg_hba.conf y httpd.conf en la misma ubicacion que este instalador.")
            #time.sleep(3)
            
        elif sys.argv[1] == "install-apache":
            pass
            distro.prinxi("Instalacion de Apache completada.")
        elif sys.argv[1] == "install-pxp":
            pass
            distro.prinxi("Instalacion de PXP completada.")
        elif sys.argv[1] == "install-php":
            pass
            distro.prinxi("Instalacion de PHP completada.")
        elif sys.argv[1] == "install-postgresql":
            pass
            distro.prinxi("Instalacion de PostgreSQL completada.")
        elif sys.argv[1] == "help":
            showHelp = True
        elif sys.argv[1] == "version":
            distro.prinxi("")
            #distro.prinxi("Instalador Framework PXP version 1.0   (c) 2013 Kplian Ltda.\n")             
        else:
            distro.prinw("ERROR: Opcion no valida.")
            showHelp = True
        
        if showHelp: 
            distro.prinxi("HELP: Ayuda del Instalador PXP Kplian\n\n"
                     "EL instalador PXP instala todos los paquetes necesarios para usar el Framework PXP Kplian,\n"
                     "incluido este ultimo. Tambien  provee  opciones  de instalacion de paquetes individuales\n"
                     "como PostgreSQL, Apache, PHP o solo el Framework PXP.\n\n"
                     "\tUSO:\n"
                     "\t   pxp.installer.py [OPCION]\n\n"
                     "\tOPCIONES:\n"
                     "\t   install-pxp           Instalar solo el Framework PXP. No se hara ninguna validacion\n"
                     "\t                         de los paquetes necesarios para que este fucione correctamente,\n"                         
                     "\t                         se asumira que ya se encuentran instalados y configurados.\n"
                     "\t   install-postgresql    Instalar solo el paquete PostgreSQL.\n"
                     "\t   install-apache        Instalar solo el paquete Apache httpd.\n"
                     "\t   install-php           Instalar solo el paquete PHP.\n"
                     "\t   help                  Muestra esta ayuda.\n"
                     "\t   version               Muestra la version del instalador.\n\n"
                     "\tEJEMPLOS:\n"
                     "\t   pxp.installer.py install-pxp         Instalara solo el Framework PXP.\n"
                     "\t   pxp.installer.py                     Instalara todos los pauqetes necesarios para comenar\n"
                     "\t                                        a desarrollar con el Framework PXP.\n"
                     "\t   pxp.installer.py install-postgresql  Instalara solo PostgreSQL.\n")        
            
            
    elif len(sys.argv) < 2:        
            distro.prini("Esta apunto de instalar el Framework PXP, esta seguro de continuar? (escriba si o no)")
            opcion = distro.readInput('si/no? [no]: ')
            if (opcion == 'si') :
                distro.prini("Iniciando instalacion del Framework PXP....... (c) 2013 Kplian Ltda.\n")
                time.sleep(1)
            else:
                distro.prinxi("Instalacion del Framework PXP  detenida.")
    else:
        distro.prinw("El programa tomara en cuenta solo el primer argumento:"+ sys.argv[1] )
        time.sleep(1)
        
    ###########################################
    
    distro.validatePrerequisites()
    print 'Analizando la distribucion, arquitectura y version...\n'
    distro.detectOS()
    #distro.installPostgres()
    #distro.installApache()
    #distro.enableNetConnections()
    distro.configureFiles()
    distro.prini("Instalacion completada.")
    

except KeyboardInterrupt:    
    if distro.PID:
        process = distro.executeSilent("ps -p "+distro.PID+" -o args=")
        cmd = distro.executeSilent("ps -p "+distro.PID+" -o comm=")
        distro.prinw("Ejecucion de comando '"+cmd.strip('\n')+"' interrumpido.")
        distro.prini("Deteniendo proceso...:\n"+process)
        distro.executeSilent("kill -9 "+distro.PID)
        distro.prinxi("bye")
    
    distro.prinw('Instalacion interrumpida/cancelada por el usuario.')
  
