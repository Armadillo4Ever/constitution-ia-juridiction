# Constitution des systèmes d'IA générative d'une juridiction, partie II : garanties techniques.
# Implémentation de référence, bibliothèque standard seulement. Chaque fonction porte le numéro
# de la garantie qu'elle exécute ; les essais correspondants sont dans essais.py.
# © 2026 Armadillo4Ever. Licence MIT (voir LICENSE).
import hashlib
import json
import re
import time
import unicodedata

VERSION = "0.2"


# ---- G2. Séparation des canaux : les pièces sont balisées par leur dénomination exacte ----------
def baliser_pieces(pieces):
    """Rend le bloc à placer dans le canal utilisateur. `pieces` : liste de {"denomination", "texte"}.
    Rien à l'intérieur d'une balise ne peut la fermer : une fausse balise de fin est neutralisée."""
    blocs = []
    for n, p in enumerate(pieces, 1):
        nom = (p.get("denomination") or "pièce sans dénomination").replace('"', "'")
        corps = re.sub(r"</\s*piece", "<\\/piece", p.get("texte") or "", flags=re.I)
        blocs.append('<piece n="%d" denomination="%s">\n%s\n</piece>' % (n, nom, corps))
    return "\n\n".join(blocs)


# ---- G3. Format de sortie contraint : une réponse hors schéma est rejetée -----------------------
class SortieInvalide(ValueError):
    pass


def valider_sortie(texte, schema):
    """`schema` : {"champ": type} ; tous les champs sont obligatoires. Rend le dict validé."""
    try:
        debut, fin = texte.index("{"), texte.rindex("}") + 1
        sortie = json.loads(texte[debut:fin])
    except (ValueError, json.JSONDecodeError) as e:
        raise SortieInvalide("réponse non conforme au format JSON attendu : %s" % e)
    for champ, typ in schema.items():
        if champ not in sortie:
            raise SortieInvalide("champ manquant : %s" % champ)
        if not isinstance(sortie[champ], typ):
            raise SortieInvalide("champ %s : %s attendu" % (champ, typ.__name__))
    return sortie


# ---- G4. Contrôle de citation : toute référence citée doit exister dans les fonds ----------------
_REF = re.compile(r"n[°o]\s*([0-9]{3,7}(?:[_\-][0-9]{3,7})*)", re.I)


def controler_citations(texte, fonds):
    """`fonds` : ensemble des numéros connus. Rend {"verifiees": [...], "inconnues": [...]}."""
    trouvees = sorted(set(m.group(1) for m in _REF.finditer(texte or "")))
    return {"verifiees": [r for r in trouvees if r in fonds],
            "inconnues": [r for r in trouvees if r not in fonds]}


def marquer_citations_inconnues(texte, inconnues):
    """Une référence absente des fonds n'est pas effacée en silence : elle est marquée."""
    for r in inconnues:
        texte = re.sub(r"(n[°o]\s*%s)" % re.escape(r), r"\1 [RÉFÉRENCE NON TROUVÉE DANS LES FONDS]", texte)
    return texte


def controler_fidelite(passage, source):
    """Le passage reproduit « mot pour mot » figure-t-il dans la source ? Comparaison tolérante
    aux espaces et à la casse, jamais au sens."""
    def plat(s):
        s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
        return re.sub(r"\s+", " ", s).strip()
    return bool(passage) and plat(passage) in plat(source)


# ---- G7. Journalisation : chaque sollicitation laisse une trace, sans le contenu des pièces ------
def empreinte(texte):
    return hashlib.sha256((texte or "").encode("utf-8")).hexdigest()[:16]


def journaliser(chemin, utilisateur, tache, versions, pieces, consigne, sortie, reprise=None):
    """Une ligne JSON par sollicitation. Les pièces et la sortie sont journalisées par empreinte,
    pas par contenu : le journal sert à retracer, pas à relire les dossiers."""
    ligne = {"horodatage": time.strftime("%Y-%m-%dT%H:%M:%S"), "utilisateur": utilisateur, "tache": tache,
             "versions": versions, "pieces": [{"denomination": p.get("denomination"),
                                                "empreinte": empreinte(p.get("texte"))} for p in pieces],
             "consigne": empreinte(consigne), "sortie": empreinte(sortie), "reprise": reprise}
    with open(chemin, "a", encoding="utf-8") as f:
        f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
    return ligne


# ---- G8. Détection à l'ingestion des instructions adressées au système ---------------------------
_MOTIFS = [
    (r"ignore[rz]?\s+(toutes?\s+)?(tes|les|vos)\s+(instructions|consignes|r[èe]gles)", "instruction adressée au système"),
    (r"(oublie|n[ée]glige)[rz]?\s+(tes|les|vos)\s+(instructions|consignes)", "instruction adressée au système"),
    (r"\b(system prompt|prompt syst[èe]me|en tant qu'?(ia|assistant|mod[èe]le))\b", "adresse au modèle"),
    (r"\b(tu dois|vous devez)\s+(conclure|annuler|rejeter|retenir|ne pas citer|taire)\b", "injonction sur le sens"),
    (r"\bne (cite|mentionne) (pas|jamais)\b.{0,60}\b(d[ée]cision|arr[êe]t|jurisprudence)\b", "injonction de silence"),
    (r"[​‌‍⁠﻿]", "caractères invisibles"),
]


def detecter_injections(texte, denomination=None):
    """Rend la liste des passages suspects, avec leur position ; ne retire rien."""
    signalements = []
    for motif, nature in _MOTIFS:
        for m in re.finditer(motif, texte or "", flags=re.I | re.S):
            d = max(0, m.start() - 60)
            signalements.append({"piece": denomination, "nature": nature, "position": m.start(),
                                 "extrait": (texte[d:m.end() + 60]).replace("\n", " ")})
    return signalements


# ---- G14. Mention d'origine : un document produit le dit, jusqu'à sa reprise --------------------
MENTION = "[Projet préparé par un système d'aide, version {v}. À vérifier et à reprendre par son auteur.]"


def mention_origine(texte, version=VERSION):
    return MENTION.format(v=version) + "\n\n" + (texte or "")


# ---- G15. Ordre et volume des sources remises au rédacteur ---------------------------------------
def ordonner_sources(lots, priorite, plafond=0):
    """`lots` : liste de (nom du fonds, résultats dans l'ordre du fonds) ; `priorite(nom)` : rang
    d'autorité (0 = le plus élevé, réservé aux textes applicables, toujours gardés). Sous plafond,
    on prend les meilleurs de chaque fonds à tour de rôle, puis on réordonne par autorité."""
    lots = sorted(enumerate(lots), key=lambda t: (priorite(t[1][0]), t[0]))
    if not plafond:
        return [s for _i, (_n, res) in lots for s in res]
    gardes, total = set(), 0
    for i, (nom, res) in lots:
        if priorite(nom) == 0:
            gardes.update((i, r) for r in range(len(res))); total += len(res)
    rang = 0
    while total < plafond:
        ajout = False
        for i, (nom, res) in lots:
            if rang < len(res) and (i, rang) not in gardes:
                gardes.add((i, rang)); total += 1; ajout = True
                if total >= plafond:
                    break
        if not ajout:
            break
        rang += 1
    return [s for i, (_n, res) in lots for r, s in enumerate(res) if (i, r) in gardes]


# ---- G16. Documents de conformité : produits à partir de données structurées, jamais inventés ----
A_COMPLETER = "[à compléter par la personne responsable]"


def document_conformite(gabarit, donnees, titre):
    """`gabarit` : liste de (rubrique, clé de donnée ou None). Chaque valeur vient de `donnees`
    (registre, journaux, résultats d'essais) et porte sa clé d'origine ; une donnée absente laisse
    la rubrique à compléter au lieu d'être devinée. Le document est un PROJET jusqu'à validation."""
    lignes = ["PROJET, non validé. %s" % titre, "Généré le %s à partir des seules données structurées ci-dessous." % time.strftime("%Y-%m-%d")]
    for rubrique, cle in gabarit:
        if cle is None or cle not in donnees or donnees[cle] in (None, "", []):
            lignes.append("%s : %s" % (rubrique, A_COMPLETER))
        else:
            v = donnees[cle]
            lignes.append("%s : %s   [source : %s]" % (rubrique, json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v, cle))
    lignes.append("Validation : nom, qualité, date, signature : %s" % A_COMPLETER)
    return "\n".join(lignes)
