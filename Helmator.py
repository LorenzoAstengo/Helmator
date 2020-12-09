#!/usr/bin/python3
import yaml
import sys
import os
from distutils.dir_util import copy_tree
import shutil

def values(text):
    global valuesFile
    f=open(valuesFile,"a")
    f.write(text)
    f.write("\n")
    f.close
def paramNamespace(data):
    data['metadata']['namespace'] = "{{ .Values.namespace }}"
def deleteNodePort(data):
    if "nodePort" in data['spec']['ports']:
        for port in data['spec']['ports']:
            del port['nodePort']
def paramReplica(data,dep):
    rep=data['spec']['replicas']
    values("  replicaCount: "+str(rep))
    data['spec']['replicas'] = "{{ .Values."+dep+".replicaCount }}"
def paramImage(data,dep):
    image=data['spec']['template']['spec']['containers'][0]['image']
    version=image.split(":")[1]
    image=image.replace(version,"")
    values("  version: "+version)
    values("  image: "+ image+"{{ .Values."+dep+".version}}")
    data['spec']['template']['spec']['containers'][0]['image'] = "{{ .Values."+dep+".image}}"
def paramNFS(data,pv):
    values("  "+pv+": "+data["spec"]["nfs"]["path"])
    data["spec"]["nfs"]["path"]="{{.Values.Pv."+pv+"}}"

def deployments(file):
    dep=os.path.splitext(os.path.basename(file))[0]
    with open(file, 'r') as f:
        data = yaml.load(f, yaml.FullLoader)
    values(dep+":")
    paramNamespace(data)
    paramReplica(data,dep)
    paramImage(data,dep)
    with open(file, 'w') as f:
        yaml.dump(data,f)
    
def gateways(file):
    with open(file, 'r') as f:
        data = yaml.load(f, yaml.FullLoader)
    paramNamespace(data)
    with open(file, 'w') as f:
        yaml.dump(data,f)
    
def persistentVolumeClaim(file):
    with open(file, 'r') as f:
        data = yaml.load(f, yaml.FullLoader)
    paramNamespace(data)
    with open(file, 'w') as f:
        yaml.dump(data,f)

def persistentVolumes(file):
    global first
    if first:
        values("Pv:")
        first=False
    with open(file, 'r') as f:
        data = yaml.load(f, yaml.FullLoader)
    if "nfs" in data["spec"]:
        pv=os.path.splitext(os.path.basename(file))[0]
        paramNFS(data,pv)
    with open(file, 'w') as f:
        yaml.dump(data,f)
    
def configMaps(file):
    with open(file, 'r') as f:
        data = yaml.load(f, yaml.FullLoader)
    paramNamespace(data)
    with open(file, 'w') as f:
        yaml.dump(data,f)
    
def secrets(file):
    with open(file, 'r') as f:
        data = yaml.load(f, yaml.FullLoader)
    paramNamespace(data)
    with open(file, 'w') as f:
        yaml.dump(data,f)

def services(file):
    with open(file, 'r') as f:
        data = yaml.load(f, yaml.FullLoader)
    paramNamespace(data)
    deleteNodePort(data)
    with open(file, 'w') as f:
        yaml.dump(data,f)

def virtualServices(file):
    with open(file, 'r') as f:
        data = yaml.load(f, yaml.FullLoader)
    paramNamespace(data)
    with open(file, 'w') as f:
        yaml.dump(data,f)

def serviceAccounts(file):
    with open(file, 'r') as f:
        data = yaml.load(f, yaml.FullLoader)
    paramNamespace(data)
    with open(file, 'w') as f:
        yaml.dump(data,f)


dirs = {   "deployments" : deployments,
           "gateways" : gateways,
           "persistentVolumeClaim" : persistentVolumeClaim,
           "persistentVolumes" : persistentVolumes,
           "secrets" : secrets,
           "services" : services,
           "virtualServices" : virtualServices,
           "serviceAccounts" : serviceAccounts,
           "configMaps" : configMaps,
}

first=True
path = sys.argv[1]
namespace=os.path.basename(os.path.normpath(path)).replace("-clean","")
if not os.path.exists('Helm'):
    os.mkdir("Helm")
if os.path.exists("Helm/"+namespace):
    shutil.rmtree("Helm/"+namespace, ignore_errors=True)    
os.mkdir("Helm/"+namespace)
os.chdir("Helm/"+namespace)
if os.path.exists("values.yaml"):
  os.remove("values.yaml")
valuesFile=os.getcwd()+"/values.yaml"
values("namespace: "+namespace)
if not os.path.exists("templates"):
    os.mkdir("templates")
copy_tree(path, "templates")
os.chdir("templates")
directories = [d for d in os.listdir(os.getcwd())]
for d in directories:
    print("*************************************")
    print(d)
    print("*************************************")
    os.chdir(d)
    for file in os.listdir(os.getcwd()):
        print(file)
        dirs[d](file)
    os.chdir("..")

