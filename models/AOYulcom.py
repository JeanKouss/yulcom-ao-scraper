from pydantic import BaseModel


class AOYulcom(BaseModel):
    """
    Appel d'offre de Yulcom
    """
    title : str # Titre de l'offre
    category : list[str] # Catégorie de profil attendu (Ex : Développeur, IT, ...)
    type : str # Type de contrat
    level : str # Niveau d'étude pour postuler à l'offre
    location : str # Lieu de travail (Ex : Ouagadougou, Remote, ...)
    starts_at : str # Date de début de l'offre
    url : str # Lien vers l'offre
    offer_ends_at : str # Date de fin de l'offre
    description : str # Description détaillée de l'offre
