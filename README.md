# Vaccine — SQL Injection Detection & Dump Tool

Outil en ligne de commande qui, à partir d'une URL, détecte les injections SQL
sur les paramètres fournis, identifie le moteur de base de données, puis extrait
le contenu de la base par injection aveugle (blind SQLi).

> ⚠️ Usage légal uniquement. N'utilisez cet outil que sur des cibles que vous
> êtes explicitement autorisé à tester (labo personnel, sites de test prévus à
> cet effet comme testasp.vulnweb.com).

## Prérequis

- Python 3.x
- Le module `requests`

Installation des dépendances :

    python3 -m venv venv
    source venv/bin/activate
    pip install requests

## Utilisation

    ./vaccine [-o FICHIER] [-X METHODE] URL

Exemples :

    # GET (méthode par défaut)
    ./vaccine "http://testasp.vulnweb.com/showforum.asp?id=2"

    # POST, avec fichier de sortie personnalisé
    ./vaccine -X POST -o resultat.json "http://cible/page?param=valeur"

> Les guillemets autour de l'URL sont nécessaires : `?` et `&` sont des
> caractères spéciaux pour le shell.

## Options

| Option | Rôle | Défaut |
|--------|------|--------|
| `URL`  | URL cible, avec les paramètres à tester dans la query string | (obligatoire) |
| `-o`   | Fichier d'archive où est écrit le dump (JSON) | `dump_db.json` |
| `-X`   | Méthode HTTP : `GET` ou `POST` | `GET` |

Les paramètres à tester sont toujours fournis dans la query string de l'URL.
En mode `POST`, l'outil les déplace automatiquement dans le corps de la requête.

## Comment ça marche

1. **Parsing** : l'URL est découpée en `base_url` (sans query) + dictionnaire
   de paramètres.
2. **Détection** : pour chaque paramètre, deux méthodes sont testées :
   - *Error-based* : ajout d'une apostrophe `'` → une réponse 500 trahit une
     requête SQL cassée.
   - *Boolean-based* : comparaison des réponses à `AND 1=1` vs `AND 1=2`
     (différence de taille de réponse).
3. **Identification du moteur** : des sondes spécifiques (`LEN` vs `LENGTH`…)
   déterminent s'il s'agit de **Microsoft SQL Server** ou **MySQL**.
4. **Extraction aveugle** : le contenu est reconstruit caractère par caractère
   via une **recherche dichotomique** sur `ASCII(SUBSTRING(...))`, en remontant
   la hiérarchie tables → colonnes → valeurs.
5. **Archivage** : le résultat est écrit en JSON dans le fichier de sortie.

## Moteurs supportés

- Microsoft SQL Server (MSSQL)
- MySQL

## Format de sortie

Le dump est un JSON imbriqué `table → colonne → [valeurs]` :

```json
{
  "threads": {
    "id": ["0", "1", "2", "3"],
    "title": ["1", "2", "3", "aaa"],
    "poster": ["admin"]
  }
}