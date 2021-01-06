import sys
import os

MAYA_LOCATION = "C:/Program Files/Autodesk/Maya2018"
PYTHON_LOCATION = MAYA_LOCATION + "/Python/Lib/site-packages"

os.environ["MAYA_LOCATION"] = MAYA_LOCATION
os.environ["PYTHONPATH"] = PYTHON_LOCATION

sys.path.append(MAYA_LOCATION)
sys.path.append(PYTHON_LOCATION)
sys.path.append(MAYA_LOCATION+"/bin")
sys.path.append(MAYA_LOCATION+"/lib")
sys.path.append(MAYA_LOCATION+"/Python")
sys.path.append(MAYA_LOCATION+"/Python/DLLs")
sys.path.append(MAYA_LOCATION+"/Python/Lib")
sys.path.append(MAYA_LOCATION+"/Python/Lib/plat-win")
sys.path.append(MAYA_LOCATION+"/Python/Lib/lib-tk")
print('\n'.join(sys.path))

import maya.standalone as standalone
standalone.initialize(name='python')

def runMaya(filePath):
    import maya.cmds as cmds
    import json

    if filePath.endswith('.ma'):
        ft = 'mayaAscii'
    elif filePath.endswith('.mb'):
        ft = 'mayaBinary'
    else:
        raise ValueError("The OpenFile action doesn't support this file type: {}".format(filePath))
    cmds.file(filePath, force=1, type=ft, open=True)

    fileDir, fileName = os.path.split(filePath)
    fileRawName, fileExt = os.path.splitext(fileName)

    data['file name'] = fileRawName
    data['file extension'] = fileExt

    allNodes = cmds.ls(nodeTypes=True)
    sceneNodes = []
    for node in allNodes:
        if cmds.ls(exactType=node):
            sceneNodes.append(node)

    for node in sceneNodes:
        getAllAttr(ntype=node)

    path = os.path.join(fileDir, fileRawName + os.extsep + 'json')

    with open(path, 'w') as f:  
        json.dump(data, f, indent=4, separators=(',', ': '))  # generate Json file

def getAllAttr(ntype=None):
    import maya.cmds as cmds
    nodes = []
    nodes.extend(cmds.ls(exactType=ntype))

    for i, node in enumerate(nodes):
        attrList = cmds.listAttr(node, k=True)
        
        if attrList is not None:  # check for non attribute nodes
            if i is 0:
                data['file info'][ntype] = {}  # create sub-index
            valList = getAllVal(node, attrList)
            
            if len(attrList) is len(valList):
                dict = {}
                for i in range(len(attrList)):
                    dict[attrList[i]] = valList[i]
            else:
                print('not match')     
            
            data['file info'][ntype][node] = dict
    
def getAllVal(node, attrList):
    import maya.cmds as cmds
    valList = []
    for attr in attrList:
        try:
            valList.append(cmds.getAttr(node+'.'+attr))
        except:
            valList.append('no value')
    return valList


if __name__ == '__main__':
    data = {
        'file name': '',
        'file extension': '',
        'file info': {
        }
    }
    filePath = sys.argv[1]
    # print('filePath' + filePath)
    runMaya(filePath)
