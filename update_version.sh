git flow release start v$1
sed -i -e "s/__version__ = '.*'/__version__ = '$1'/g" NAME/__init__.py
git commit NAME/__init__.py -M "Update to version v$1"
git flow release finish v$1
