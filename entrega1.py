#!/usr/bin/python

import os
import os.path
import sys
import subprocess
import time
from lxml import etree
from subprocess import Popen
from string import Template
import time

#maquinas virtuales que se crearan
MaquinaVirt = ["c1", "lb", "s1","s2","s3","s4","s5"]
NumeroSer = ["s1","s2","s3","s4","s5"]

def monitorizar():
	time.sleep(5)
	os.system("sudo virsh list --all") 

def crear():

	#creamos ficheros imagenes para las maquinas
	if numeroM <= 5:
		os.system("qemu-img create -f qcow2 -b cdps-vm-base-p3.qcow2 "+ MaquinaVirt[0] + ".qcow2")
		os.system("qemu-img create -f qcow2 -b cdps-vm-base-p3.qcow2 "+ MaquinaVirt[1] + ".qcow2")
		for i in range (0, numeroM):
			os.system("qemu-img create -f qcow2 -b cdps-vm-base-p3.qcow2 "+ NumeroSer[i] + ".qcow2")
		print ("imagenes creadas")
	else:
	    os.system("qemu-img create -f qcow2 -b cdps-vm-base-p3.qcow2 "+ MaquinaVirt[0] + ".qcow2")
	    os.system("qemu-img create -f qcow2 -b cdps-vm-base-p3.qcow2 "+ MaquinaVirt[1] + ".qcow2")
	    os.system("qemu-img create -f qcow2 -b cdps-vm-base-p3.qcow2 "+ NumeroSer[0] + ".qcow2")
	    os.system("qemu-img create -f qcow2 -b cdps-vm-base-p3.qcow2 "+ NumeroSer[1] + ".qcow2")
	
	archivo = open("numero_servidores.txt", "w")
	archivo.write(str(numeroM))
	archivo.close()

	#crear plantillas xml para servidor
	tree = etree.parse('plantilla-vm-p3.xml')
	root = tree.getroot()
	name = root.find("name")
	Sersource = root.find("./devices/disk/source")
	Serinterface = root.find("./devices/interface/source")
	
	
	if numeroM <=5:
		for i in range (0, numeroM):
			Serinterface.set("bridge","LAN2")
			name.text = NumeroSer[i]
			Sersource.set("file", "/mnt/tmp/pfinalp1/" + NumeroSer[i] +".qcow2")
			tree.write(NumeroSer[i] + ".xml")
	else:
		for i in range (0, 2):
			Serinterface.set("bridge","LAN2")
			name.text = NumeroSer[i]
			Sersource.set("file", "/mnt/tmp/pfinalp1/" + NumeroSer[i] +".qcow2")
			tree.write(NumeroSer[i] + ".xml")
	
	#crear plantillas xml para c1
	Serinterface.set("bridge","LAN1")
	name.text = MaquinaVirt[0]
	Sersource.set("file", "/mnt/tmp/pfinalp1/" + MaquinaVirt[0] +".qcow2")
        tree.write(MaquinaVirt[0] + ".xml")
	
	#crear plantillas xml para lb
	Serinterface.set("bridge","LAN1")
	name.text = MaquinaVirt[1]
	Sersource.set("file", "/mnt/tmp/pfinalp1/" + MaquinaVirt[1] +".qcow2")
	devices = root.find("devices")
	interface2 = etree.SubElement(devices,"interface")
	source = etree.SubElement(interface2,"source")
	interface2.set("type","bridge")
	source.set("bridge","LAN2")
	modelinterface2= etree.SubElement(interface2,"model")
	modelinterface2.set("type","virtio")
	tree.write(MaquinaVirt[1] + ".xml")

	#creamos los bridges
	os.system("sudo brctl addbr LAN1")
	os.system("sudo brctl addbr LAN2")
	os.system("sudo ifconfig LAN1 up")
	os.system("sudo ifconfig LAN2 up")

        #creamos configuracion 
	
	for i in range(0, numeroM +2):
		os.system("mkdir mnt")
		os.system("sudo vnx_mount_rootfs -s -r "+ MaquinaVirt[i] +".qcow2 mnt")

		if MaquinaVirt[i] == MaquinaVirt[0] :
			fichero1 = open(os.getcwd() + "/mnt/etc/network/interfaces" , "r")
			fichero2 = open(os.getcwd() + "/mnt/etc/network/interfacesCambiado" , "w")

			for line in fichero1:
				if "source /etc/network/interfaces.d/*.cfg" in line:
					fichero2.write("auto eth0 \n iface eth0 inet static \n address 10.0.1.2 \n netmask 255.255.255.0 \n gateway 10.0.1.1 \n")
				else : fichero2.write(line)
			subprocess.call("mv /mnt/tmp/pfinalp1/mnt/etc/network/interfacesCambiado /mnt/tmp/pfinalp1/mnt/etc/network/interfaces", shell=True)
			fichero1.close()
			fichero2.close()
			fichero = open(os.getcwd() +"/mnt/etc/hostname" , "w")
			fichero.write("c1")
			fichero.close()

			fichero3 = open(os.getcwd() + "/mnt/etc/hosts" , "r")
			fichero4 = open (os.getcwd() + "/mnt/etc/hostsCambiado" , "w")

			for line in fichero3 :
				if "127.0.1.1 cdps" in line:
					fichero4.write("127.0.1.1 c1")
				else:
					fichero4.write(line)
	
			fichero3.close()
			fichero4.close()
			

		if MaquinaVirt[i] == MaquinaVirt[1] :
			fichero1 = open(os.getcwd() + "/mnt/etc/network/interfaces" , "r")
			fichero2 = open(os.getcwd() + "/mnt/etc/network/interfacesCambiado" , "w")

			for line in fichero1:
				if "source /etc/network/interfaces.d/*.cfg" in line:
					fichero2.write("auto eth0 \n iface eth0 inet static \n address 10.0.1.1 \n netmask 255.255.255.0 \n")
					fichero2.write("auto eth1 \n iface eth1 inet static \n address 10.0.2.1 \n netmask 255.255.255.0 \n")
				else : fichero2.write(line)
			subprocess.call("mv /mnt/tmp/pfinalp1/mnt/etc/network/interfacesCambiado /mnt/tmp/pfinalp1/mnt/etc/network/interfaces", shell=True)
			fichero1.close()
			fichero2.close()
			fichero = open(os.getcwd() +"/mnt/etc/hostname" , "w")
			fichero.write("lb")
			fichero.close()

			fichero3 = open(os.getcwd() + "/mnt/etc/hosts" , "r")
			fichero4 = open (os.getcwd() + "/mnt/etc/hostsCambiado" , "w")

			for line in fichero3 :
				if "127.0.1.1 cdps" in line:
					fichero4.write("127.0.1.1 lb")
				else:
					fichero4.write(line)
	
			fichero3.close()
			fichero4.close()
			

		if MaquinaVirt[i] == MaquinaVirt[2] :
			fichero1 = open(os.getcwd() + "/mnt/etc/network/interfaces" , "r")
			fichero2 = open(os.getcwd() + "/mnt/etc/network/interfacesCambiado" , "w")

			for line in fichero1:
				if "source /etc/network/interfaces.d/*.cfg" in line:
					fichero2.write("auto eth0 \n iface eth0 inet static \n address 10.0.2.11 \n netmask 255.255.255.0 \n gateway 10.0.2.1 \n")
				else : fichero2.write(line)
			subprocess.call("mv /mnt/tmp/pfinalp1/mnt/etc/network/interfacesCambiado /mnt/tmp/pfinalp1/mnt/etc/network/interfaces", shell=True)
			fichero1.close()
			fichero2.close()
			fichero = open(os.getcwd() +"/mnt/etc/hostname" , "w")
			fichero.write("s1")
			fichero.close()
			
			fichero3 = open(os.getcwd() + "/mnt/etc/hosts" , "r")
			fichero4 = open (os.getcwd() + "/mnt/etc/hostsCambiado" , "w")

			for line in fichero3 :
				if "127.0.1.1 cdps" in line:
					fichero4.write("127.0.1.1 s1")
				else:
					fichero4.write(line)
	
			fichero3.close()
			fichero4.close()
			

		if MaquinaVirt[i] == MaquinaVirt[3] :
			fichero1 = open(os.getcwd() + "/mnt/etc/network/interfaces" , "r")
			fichero2 = open(os.getcwd() + "/mnt/etc/network/interfacesCambiado" , "w")

			for line in fichero1:
				if "source /etc/network/interfaces.d/*.cfg" in line:
					fichero2.write("auto eth0 \n iface eth0 inet static \n address 10.0.2.12 \n netmask 255.255.255.0 \n gateway 10.0.2.1 \n")
				else : fichero2.write(line)
			subprocess.call("mv /mnt/tmp/pfinalp1/mnt/etc/network/interfacesCambiado /mnt/tmp/pfinalp1/mnt/etc/network/interfaces", shell=True)		
			fichero1.close()
			fichero2.close()
			fichero = open(os.getcwd() +"/mnt/etc/hostname" , "w")
			fichero.write("s2")
			fichero.close()

			fichero3 = open(os.getcwd() + "/mnt/etc/hosts" , "r")
			fichero4 = open (os.getcwd() + "/mnt/etc/hostsCambiado" , "w")

			for line in fichero3 :
				if "127.0.1.1 cdps" in line:
					fichero4.write("127.0.1.1 s2")
				else:
					fichero4.write(line)
	
			fichero3.close()
			fichero4.close()
			

		if MaquinaVirt[i] == MaquinaVirt[4] :
			fichero1 = open(os.getcwd() + "/mnt/etc/network/interfaces" , "r")
			fichero2 = open(os.getcwd() + "/mnt/etc/network/interfacesCambiado" , "w")

			for line in fichero1:
				if "source /etc/network/interfaces.d/*.cfg" in line:
					fichero2.write("auto eth0 \n iface eth0 inet static \n address 10.0.2.13 \n netmask 255.255.255.0 \n gateway 10.0.2.1 \n")
				else : fichero2.write(line)
			subprocess.call("mv /mnt/tmp/pfinalp1/mnt/etc/network/interfacesCambiado /mnt/tmp/pfinalp1/mnt/etc/network/interfaces", shell=True)		
			fichero1.close()
			fichero2.close()
			fichero = open(os.getcwd() +"/mnt/etc/hostname" , "w")
			fichero.write("s3")
			fichero.close()

			fichero3 = open(os.getcwd() + "/mnt/etc/hosts" , "r")
			fichero4 = open (os.getcwd() + "/mnt/etc/hostsCambiado" , "w")

			for line in fichero3 :
				if "127.0.1.1 s3" in line:
					fichero4.write("127.0.1.1 s3")
				else:
					fichero4.write(line)
	
			fichero3.close()
			fichero4.close()
			

		if MaquinaVirt[i] == MaquinaVirt[5] :
			fichero1 = open(os.getcwd() + "/mnt/etc/network/interfaces" , "r")
			fichero2 = open(os.getcwd() + "/mnt/etc/network/interfacesCambiado" , "w")

			for line in fichero1:
				if "source /etc/network/interfaces.d/*.cfg" in line:
					fichero2.write("auto eth0 \n iface eth0 inet static \n address 10.0.2.14 \n netmask 255.255.255.0 \n gateway 10.0.2.1")
				else : fichero2.write(line)
			subprocess.call("mv /mnt/tmp/pfinalp1/mnt/etc/network/interfacesCambiado /mnt/tmp/pfinalp1/mnt/etc/network/interfaces", shell=True)	
			fichero1.close()
			fichero2.close()
			fichero = open(os.getcwd() +"/mnt/etc/hostname" , "w")
			fichero.write("s4")
			fichero.close()

			fichero3 = open(os.getcwd() + "/mnt/etc/hosts" , "r")
			fichero4 = open (os.getcwd() + "/mnt/etc/hostsCambiado" , "w")

			for line in fichero3 :
				if "127.0.1.1 cdps" in line:
					fichero4.write("127.0.1.1 s4")
				else:
					fichero4.write(line)
	
			fichero3.close()
			fichero4.close()

			

		if MaquinaVirt[i] == MaquinaVirt[6] :
			fichero1 = open(os.getcwd() + "/mnt/etc/network/interfaces" , "r")
			fichero2 = open(os.getcwd() + "/mnt/etc/network/interfacesCambiado" , "w")

			for line in fichero1:
				if "source /etc/network/interfaces.d/*.cfg" in line:
					fichero2.write("auto eth0 \n iface eth0 inet static \n address 10.0.2.15 \n netmask 255.255.255.0 \n gateway 10.0.2.1 \n")
				else : fichero2.write(line)
			subprocess.call("mv /mnt/tmp/pfinalp1/mnt/etc/network/interfacesCambiado /mnt/tmp/pfinalp1/mnt/etc/network/interfaces", shell=True)		
			fichero1.close()
			fichero2.close()
			fichero = open(os.getcwd() +"/mnt/etc/hostname" , "w")
			fichero.write("s5")
			fichero.close()

			fichero3 = open(os.getcwd() + "/mnt/etc/hosts" , "r")
			fichero4 = open (os.getcwd() + "/mnt/etc/hostsCambiado" , "w")

			for line in fichero3 :
				if "127.0.1.1 cdps" in line:
					fichero4.write("127.0.1.1 s5")
				else:
					fichero4.write(line)
	
			fichero3.close()
			fichero4.close()
		ficherolb = open(os.getcwd() + "/mnt/etc/sysctl.conf", "w")
		ficherolb.write("sysctl net.ipv4.ip_forward \n net.ipv4.ip_forward = 1 \n cat /proc/sys/net/ipv4/ip_forward \n 1")
		ficherolb.close()
		os.system("sudo vnx_mount_rootfs -u mnt")

	print("ESCENARIO CREADO")
 
	return	

def arrancar():

	archivo = open("numero_servidores.txt", "r")
	numero= int(archivo.read()) 
	archivo.close()
	if(os.path.exists("/mnt/tmp/pfinalp1/c1.qcow2") and os.path.exists("/mnt/tmp/pfinalp1/lb.qcow2")):
		for i in range(0,numero + 2):
			os.system("sudo virsh define " + MaquinaVirt[i] +".xml")
			os.system("sudo virsh start " + MaquinaVirt[i])
			os.system("sudo ifconfig LAN1 10.0.1.3/24")
			os.system("sudo ip route add 10.0.0.0/16 via 10.0.1.1")
			os.system("xterm -e 'sudo virsh console " + MaquinaVirt[i] + "' &")
	
	return

def parar():
	archivo = open("numero_servidores.txt", "r")
	numero= int(archivo.read()) 
	archivo.close()
	
	for i in range(0, numero +2):
		os.system("sudo virsh shutdown " + MaquinaVirt[i])
	return

def destruir():
	archivo = open("numero_servidores.txt", "r")
	numero= int(archivo.read()) 
	archivo.close()
	
	for i in range(0, numero +2):
		
		os.system("sudo virsh destroy " + MaquinaVirt[i])
		os.system("sudo virsh undefine " + MaquinaVirt[i])
		os.system("rm " + MaquinaVirt[i] + ".qcow2 -f")
		os.system("rm " + MaquinaVirt[i] + ".xml -f")
	
	
      	return
	


	
 
accion = sys.argv[1]
if accion == "crear":
	if(len(sys.argv)== 3 and sys.argv[2].isdigit()):
		numeroM = int(sys.argv[2])
		crear()
	if(len(sys.argv)== 2 and sys.argv[1]== "crear"):
		numeroM = 2		
		crear()
	if(len(sys.argv)== 3 and sys.argv[2] == "monitorizar"):
		numeroM=2
		crear()
		monitorizar()
	if(len(sys.argv)== 4 and sys.argv[1]== "crear" and sys.argv[3]=="monitorizar"):
		numeroM = int(sys.argv[2])
		crear()
		monitorizar()
elif accion == "arrancar":
	if(len(sys.argv)== 2 and sys.argv[1]== "arrancar"):
		arrancar()
	if(len(sys.argv)==3 and sys.argv[1]=="arrancar" and sys.argv[2]=="monitorizar"):
		arrancar()
		monitorizar()
elif accion == "parar":
	if(len(sys.argv)== 2 and sys.argv[1]== "parar"):
		parar()
	if(len(sys.argv)==3 and sys.argv[1]=="parar" and sys.argv[2]=="monitorizar"):
		parar()
		monitorizar()
elif accion == "destruir":
	if(len(sys.argv)== 2 and sys.argv[1]== "destruir"):
		destruir()
	if(len(sys.argv)==3 and sys.argv[1]=="destruir" and sys.argv[2]=="monitorizar"):
		destruir()
		monitorizar()


	
	
		 
	
