import itertools


class EmailGenerator:
    def __init__(self):
        pass

    def generer_variants_email(self, nom_propre, domaine):
        prenoms, noms = nom_propre.split() if ' ' in nom_propre else (nom_propre, '')
        prenoms = prenoms.lower()
        noms = noms.lower()
        prenoms_sans_espaces = prenoms.replace(' ', '')

        # Créer différentes combinaisons possibles
        variations = [
            f"{prenoms}.{noms}@{domaine}",
            f"{prenoms}{noms}@{domaine}",
            f"{prenoms}.{noms[0]}@{domaine}",
            f"{prenoms}{noms[0]}@{domaine}",
            f"{noms}@{domaine}",
            f"{noms[0]}@{domaine}",
            f"{prenoms_sans_espaces}@{domaine}"
        ]

        return variations

    def generer_emails_pour_noms_propres(self, noms_propres, domaine):
        emails = {}
        for nom_propre in noms_propres:
            variants = self.generer_variants_email(nom_propre, domaine)
            emails[nom_propre] = variants
        return emails


if __name__ == "__main__":
    email_gen = EmailGenerator()

    noms_propres = ["Louis Bedeschi", "Samy Difallah"]
    domaine = "blabla.com"

    resultats = email_gen.generer_emails_pour_noms_propres(noms_propres, domaine)

    for nom_propre, emails in resultats.items():
        print(f"Emails pour {nom_propre}:")
        for email in emails:
            print(email)
        print()
