system_message_style = """
    Réponds à la question avec exactement 3 mots.
    Suis le format:
    1. mot1
    2. mot2
    3. mot3
    """


user_message_style_1 = """
    Décris en 3 mots le style linguistique de ce message ?
    """


user_message_style_2 = """
    Décris en 3 mots le ton de ce message ?
    """


system_message_register = """
    Réponds à la question avec l'un des 3 mots: soutenu, courant ou familier.
    Suis le format:
    1. mot
    """


user_message_register = """
    Ce message a-t-il un niveau de langage élevé, courant ou familier ?
    """


email_template = """
    Madame, Monsieur,
    Je me permets de vous écrire afin de vous informer que j'ai fondé mon entreprise il y a maintenant un an.
    Nous avons connu de nombreux succès en France et nous envisageons désormais de nous étendre à l'international.
    Dans ce cadre, je souhaiterais vous proposer de prendre part à cette nouvelle étape en investissant au capital de notre société.
    Je me tiens à votre disposition pour discuter plus en détail de cette opportunité.
    Veuillez agréer, Madame, Monsieur, l'expression de mes salutations distinguées.
    """


system_message_email = """
    [sender] écrit à [recipient].
    La réponse doit être générée avec un niveau de langage [register].
    La réponse contient seulement le message.
    """


user_message_email = """
    Ré-écris le message suivant en lui donnant un style [style1], [style2] et [style3]:
    [email_template][sender]
    """


system_message_email_alt = """
    Tu es un des membres fondateurs d'une entreprise.
    Tu es compétent dans l'analyse de texte et tu sais étudier un texte pour en définir le niveau de langage et le ton.

    Voici un exemple représentatif du style:
    [example]

    [sender] écrit [recipient].
    La réponse contient seulement le message.
    """


user_message_email_alt = """
    Ré-écris le message suivant avec le même style que dans l'exemple:
    [email_template][sender]
    """
