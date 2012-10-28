Calcul de statistiques pour camptocamp.org
==========================================

c2cstats est une application web qui permet de calculer des statistiques pour
la liste de sorties d'un utilisateur de [camptocamp.org](http://camptocamp.org/).

La partie serveur est réalisée avec [Flask](http://flask.pocoo.org/) et
renvoie les statistiques au format json. La partie cliente est en javascript,
les graphiques étant réalisés avec [Flot](http://www.flotcharts.org/).

Installation (avec virtualenv):

    virtualenv venv
    pip install -r requirements.txt

Lancement du serveur de développement:

    python2 manage.py runserver

Lancement d'une console pré-configurée (avec l'application ``app`` et la
méthode pour générer les données ``generate``):

    python2 manage.py shell
