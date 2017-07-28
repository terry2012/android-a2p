import sys
import re
import os

def readManifest(javasrc):
    name_to_permission = {}
    pattern = re.compile(r'([A-Z_]+)=\"([A-Za-z_\.]+)\"')
    for m in re.findall(pattern, javasrc):
        name_to_permission[m[0]] = m[1]
    return name_to_permission

def hasPermission(javasrc):
    if '@RequiresPermission' in javasrc:
        return True
    elif '@link android.Manifest.permission' in javasrc:
        return True
    return False

def getMethodName(line):
    pattern = re.compile(r'\s+([a-z][A-Za-z0-9_]*)\(')
    m = pattern.search(line, re.MULTILINE)
    if m:
        return m.group(1)
    return ''

def getPermissionFromDoc(docstr):
    pattern = re.compile(r'\{@link\sandroid\.Manifest\.permission\#([A-Z_]+)[^\}]*\}')
    permissions = set()
    for m in re.findall(pattern, docstr):
        permissions.add(m)
    return ','.join(permissions)

def handlePermission(permission, name_to_permission):
    res = permission.replace(' ', '').replace('\n', '').replace('android.Manifest.permission.', '').replace('Manifest.permission.', '')
    all_pattern = re.compile(r'allOf={([^}]+)}')
    any_pattern = re.compile(r'anyOf={([^}]+)}')
    is_any = True
    allm = re.match(all_pattern, res)
    if allm:
        is_any = False
        res = allm.group(1)
    anym = re.match(any_pattern, res)
    if anym:
        res = anym.group(1)
    ps = set()
    for p in res.split(','):
        full = name_to_permission.get(p)
        if not full:
            print "not find: " + p
        else:
            ps.add(full)
    if is_any:
        res = '|'.join(ps)
    else:
        res = '&'.join(ps)
    return res

def parseJavaSource(cname, javasrc, mapping, name_to_permission):
    pkg_pattern = re.compile(r'package\s([^;\s]+)')
    pkg_m = re.search(pkg_pattern, javasrc)
    fqn = cname
    if pkg_m:
        fqn = pkg_m.group(1) + '.' + cname
    anno_pattern = re.compile(r'@RequiresPermission\(([^\)]*)\)(([^/;])+?(?=;))')
    for m in re.findall(anno_pattern, javasrc):
        permission = m[0]
        method = getMethodName(m[1])
        full_permissions = handlePermission(permission, name_to_permission)
        if full_permissions:
            item = fqn + ' ' + method + ' ' + full_permissions
            mapping.add(item)
    doc_pattern = re.compile(r'(/\*\*(?:[^*]|\*(?!/))*\*/)(([^/;])+?(?=;))')
    for m in re.findall(doc_pattern, javasrc):
        permission = getPermissionFromDoc(m[0])
        if permission:
            method = getMethodName(m[1])
            if method:
                full_permissions = handlePermission(permission, name_to_permission)
                if full_permissions:
                    item = fqn + ' ' + method + ' ' + full_permissions
                    mapping.add(item)

rootdir = sys.argv[1]
name_to_permission = {}
for root, dirs, files in os.walk(rootdir):
    for file in files:
        if file == 'Manifest.java':
            file_path = os.path.join(root, file)
            with open(file_path) as manifest:
                code = manifest.read()
                name_to_permission.update(readManifest(code))
            break

mapping = set()
for root, dirs, files in os.walk(rootdir):
    for file in files:
        if file.endswith(".java"):
            file_path = os.path.join(root, file)
            with open(file_path) as java:
                code = java.read()
                if hasPermission(code):
                    cname = file.replace('.java', '')
                    parseJavaSource(cname, code, mapping, name_to_permission)

outfile = open('mapping.txt', 'w+')
for item in mapping:
    outfile.write('%s\n' % item)

