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


## Notes pour la mise à jour sur le serveur

[Config du serveur](https://dev.camptocamp.org/trac/c2corg/browser/trunk/infrastructure/puppetmaster/site-modules/c2corg/manifests/stats.pp)

Mise à jour:

    cd /usr/src/c2c-stats
    sudo -u c2corg git pull
    sudo service gunicorn restart

En cas de modification du requirements.txt, il mettre à jour le virtualenv
avant de redémarrer gunicorn. Comme le virtualenv est géré par puppet, il faut
forcer son exécution:

    sudo puppet agent -t

En cas de modification des stats json ou des pages html, il faut vider le cache:

    sudo find /var/lib/c2cstats/cache/ -type f -delete
