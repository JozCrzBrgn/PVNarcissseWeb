

#? make pip PKG="supabase"
pip:
# Instalar librerias en venv/  y guardar librerias en requirements.txt
	@if [ ! -f requirements.txt ]; then \
		touch requirements.txt; \
	fi
	pip install $(PKG) && pip freeze | grep $(PKG) >> requirements.txt

#? make feat BRANCH="dev"
feat:
# Creamos un nuevo componente
	git checkout develop
	git pull origin develop
	git checkout -b feat/$(BRANCH) develop

#? make mdev BRANCH="dev"
mdev:
# Hacemos un merge de feat a develop
	git checkout develop
	git pull origin develop
	git merge feat/$(BRANCH)

mmain:
# Hacemos un merge de develop a main
	git checkout main
	git pull origin main
	git merge develop

#? make tag MSG="escribe-un-mensaje"
tag:
# Hacemos un merge de develop a main
	git tag -a login -m "$(MSG)"
	git push --tags

run:
# Corremos la app
	streamlit.exe run streamlit_app.py

#? make cred NAMES="['Josefina', 'Bob', 'Charlie']" USRN="['alice123', 'bob456', 'charlie789']" PSS="['pass1', 'pass2', 'pass3']"
cred:
# Creamos las credenciales
	@py -c "from config.generate_keys import crear_credenciales; crear_credenciales($(NAMES), $(USRN), $(PSS))";