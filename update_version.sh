git stash
git flow release start v$1
sed -i -e "s/__version__ = '.*'/__version__ = '$1'/g" django_egfk/__init__.py
git commit django_egfk/__init__.py -m "Update to version v$1"
git flow release finish v$1
git stash pop
