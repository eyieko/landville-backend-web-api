from os import getcwd, listdir, path, system

original_directory = getcwd()

"""
apps is a list which contains the projects apps names with fixtures you want to load,
Therefore, in case you want to add new app with fixtures to load, 
simply add the app (folder) name  in the apps list.
"""

apps = ['authentication', 'property', 'pages']
files = []


def loaddata(file):
    if path.splitext(file)[1] == '.json' and file != 'initial_data.json':
        system(f'python3 manage.py loaddata {file}')


for app in apps:
    files = listdir(f'{original_directory}/{app}/fixtures')
    files.sort()
    if files:
        list(map(loaddata, files))
