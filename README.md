# EMAIL WRITER

.env file content
```
MISTRAL_API_KEY=???
MISTRAL_CACHE_DUMP=full_path_to_mistral_cache_dump.json
MISTRAL_LOGGING_FILE=full_path_to_mistral.log
```

Tous les modules ont été testé avec Python 3.10.13.

# Mistral
Mistral API Wrapper (cache + logging).  
Affiche quelques exemples de questions posées à Mistral AI.  
```
python3 -m venv mistral
cd mistral
source bin/activate
pip install python-dotenv
pip install mistralai
ln -s ../.env .env
python3 main.py
```

# Pandas
Affiche l'exploration initiale du fichier emails-ref.json.  
Supprime les emails dont on ne peut pas identifier l'émetteur ou destinataire.  
Dans le cadre de l'exercice on identifie une personne par son prénom.  
Formate le fichier json en groupant les emails par couple émetteur/destinataire.  

Entrée: ./pandas/emails-ref.json  
Sortie: ./pandas/emails-clean.json  
```
python3 -m venv pandas
cd pandas
source bin/activate
pip install icecream
pip install jsonschema
pip install mistralai
pip install pandas
pip install python-dotenv  
ln -s ../.env .env
python3 main.py
```

# Screening
Supprime les contacts jugés non pertinents.  
Dans le cadre de l'exercice on considère que les membres de la famille proche ne sont pas des cibles pertinentes.  
Conserve uniquement les contacts jugés pertinents.  
Dans le cadre de l'exercice on considère que seuls les amis et les relations professionnelles sont des cibles pertinentes.  
Supprime les contacts avec qui il y a eu au moins un email délicat.  
Affiche les emails (différents) sélectionnés.

Entrée: ./screening/emails-clean.json  
Sortie: ./screening/emails-screening.json
```
python3 -m venv screening
cd screening
source bin/activate
pip install python-dotenv  
pip install mistralai
ln -s ../.env .env
python3 main.py
```

# Writer
Extrait, pour chaque couple émetteur/destinataire, les 3 qualificatifs de style les plus couramment utilisés ainsi que le registre de langage le plus fréquent.  
Pour chaque couple émetteur/destinataire, réécrit le template en appliquant les styles et le registre de langage.  
Réécrit le template en s'inpirant directement des émails reçus.  
Affiche les emails (différents) générés.

Input: ./writer/emails-screening.json  
Output: ./writer/emails-final.json
```
python3 -m venv writer
cd writer
source bin/activate
pip install python-dotenv  
pip install mistralai
ln -s ../.env .env
python3 main.py
```

# Pandas2
Supprime les émails en doublon.  
Extrait de chaque email:
* l'émetteur,
* le nom de l'émetteur,
* le destinataire,
* le nom du destinataire,
* le lien entre l'émetteur et le destinataire.
Affiche le dataframe.  

Entrée: ./pandas/emails-ref.json  
Sortie: ./pandas/emails-clean.json  
```
python3 -m venv pandas
cd pandas
source bin/activate
pip install mistralai
pip install pandas
pip install python-dotenv  
ln -s ../.env .env
python3 main.py
```

# Writer2
Coming soon...
