user_message_extract_infos_1 = """
"[message]"

Décris une procédure en 7 points permettant d'identifier l'auteur du message, le prénom de l'auteur, le destinataire du message, le prénom du destinataire, le lien entre l'auteur et le destinataire.
Réponds à tous les points de la procédure.
Suis le format:
Procédure:
1. Description
   Réponse:
2. Description
   Réponse:
3. Description
   Réponse:
4. Description
   Réponse:
5. Description
   Réponse:
6. Description
   Réponse:
7. Description
   Réponse:
"""


user_message_extract_infos_2 = """
"[message]"

Informations:
[info1]
[info2]
[info3]
[info4]
[info5]
[info6]
[info7]

A partir du message et des informations, identifie l'auteur du message, le prénom de l'auteur, le destinataire du message, le prénom du destinataire, le lien entre l'auteur et le destinataire.
Réponds Inconnu si tu ne sais pas.
Réponds à toutes les questions en moins de 4 mots.
Suis le format:
Réponses:
1. Auteur du message
   Réponse:
2. Prénom de l'auteur
   Réponse:
3. Destinataire du message
   Réponse:
4. Prénom du destinataire
   Réponse:
5. Lien entre l'auteur et le destinataire
   Réponse:
"""
