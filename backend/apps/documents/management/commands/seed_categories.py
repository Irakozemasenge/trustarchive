from django.core.management.base import BaseCommand
from apps.documents.models import DocumentCategory


class Command(BaseCommand):
    help = 'Creer les categories de documents par defaut'

    def handle(self, *args, **kwargs):
        categories = [
            {'name': 'Diplome universitaire', 'description': 'Licences, Masters, Doctorats', 'icon': 'FiAward'},
            {'name': 'Attestation de travail', 'description': 'Certificats emploi et experience', 'icon': 'FiBriefcase'},
            {'name': 'Acte notarie', 'description': 'Actes authentiques notaries', 'icon': 'FiFileText'},
            {'name': 'Certificat de naissance', 'description': 'Etat civil - naissance', 'icon': 'FiUser'},
            {'name': 'Certificat de mariage', 'description': 'Etat civil - mariage', 'icon': 'FiHeart'},
            {'name': 'Casier judiciaire', 'description': 'Extrait de casier judiciaire', 'icon': 'FiShield'},
            {'name': 'Permis de conduire', 'description': 'Permis de conduire officiel', 'icon': 'FiTruck'},
            {'name': 'Carte nationale identite', 'description': 'CNI officielle', 'icon': 'FiCreditCard'},
            {'name': 'Passeport', 'description': 'Document de voyage', 'icon': 'FiGlobe'},
            {'name': 'Certificat medical', 'description': 'Documents medicaux officiels', 'icon': 'FiActivity'},
            {'name': 'Contrat de travail', 'description': 'Contrats emploi certifies', 'icon': 'FiClipboard'},
            {'name': 'Autre document', 'description': 'Autres documents officiels', 'icon': 'FiFile'},
        ]

        created = 0
        for cat in categories:
            obj, is_new = DocumentCategory.objects.get_or_create(
                name=cat['name'],
                defaults={'description': cat['description'], 'icon': cat['icon']}
            )
            if is_new:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'  + {cat["name"]}'))
            else:
                self.stdout.write(f'  = {cat["name"]} (existe deja)')

        self.stdout.write(self.style.SUCCESS(f'\n{created} categorie(s) creee(s).'))
