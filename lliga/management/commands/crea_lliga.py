from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from datetime import timedelta
from random import randint, choice

from lliga.models import Lliga, Equip, Jugador, Partit, Event

faker = Faker(["es_CA", "es_ES"])


class Command(BaseCommand):
    help = 'Crea una lliga amb equips, jugadors, partits i gols'

    def add_arguments(self, parser):
        parser.add_argument('titol_lliga', nargs=1, type=str)

    def handle(self, *args, **options):
        titol_lliga = options['titol_lliga'][0]

        if Lliga.objects.filter(titol=titol_lliga).exists():
            self.stdout.write("Aquesta lliga ja està creada. Posa un altre nom.")
            return

        # --- Crear lliga ---
        self.stdout.write(f"Creem la nova lliga: {titol_lliga}")
        lliga = Lliga(titol=titol_lliga, temporada="2024-25")
        lliga.save()

        # --- Crear equips i jugadors ---
        equips = []
        prefixos = ["RCD", "Athletic", "", "Deportivo", "Unión Deportiva", "CF", "FC"]
        for i in range(10):  # 10 equips per agilitzar
            ciutat = faker.city()
            prefix = choice(prefixos)
            nom = f"{prefix} {ciutat}".strip()
            equip = Equip(ciutat=ciutat, nom=nom, lliga=lliga)
            equip.save()
            equips.append(equip)
            self.stdout.write(f"  Equip: {nom}")

            for dorsal in range(1, 16):  # 15 jugadors per equip
                jugador = Jugador(
                    nom=faker.first_name(),
                    cognom=faker.last_name(),
                    dorsal=dorsal,
                    posicio=choice(["Porter", "Defensa", "Migcampista", "Davanter"]),
                    equip=equip,
                )
                jugador.save()

        # --- Crear partits i gols ---
        self.stdout.write("Creem partits i gols...")
        data_inici = timezone.now() - timedelta(weeks=20)

        for jornada, local in enumerate(equips):
            for visitant in equips:
                if local == visitant:
                    continue

                partit = Partit(
                    local=local,
                    visitant=visitant,
                    lliga=lliga,
                    jornada=jornada + 1,
                    inici=data_inici + timedelta(weeks=jornada, hours=randint(16, 21)),
                )
                partit.save()

                # Gols local
                jugadors_local = list(local.jugador_set.all())
                for _ in range(randint(0, 4)):
                    jugador = choice(jugadors_local)
                    Event(
                        partit=partit,
                        tipus=Event.EventType.GOL,
                        jugador=jugador,
                        equip=local,
			temps=f"{randint(0,1):02d}:{randint(0,59):02d}:00",
                    ).save()

                # Gols visitant
                jugadors_visitant = list(visitant.jugador_set.all())
                for _ in range(randint(0, 4)):
                    jugador = choice(jugadors_visitant)
                    Event(
                        partit=partit,
                        tipus=Event.EventType.GOL,
                        jugador=jugador,
                        equip=visitant,
			temps=f"{randint(0,1):02d}:{randint(0,59):02d}:00",
                    ).save()

        self.stdout.write(self.style.SUCCESS(f"✅ Lliga '{titol_lliga}' creada amb èxit!"))
