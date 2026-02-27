from django.core.management.base import BaseCommand
from faker import Faker
from random import randint, choice
from datetime import datetime, timedelta

from futbol.models import Lliga, Equip, Jugador, Partit, Event

faker = Faker(["es_CA","es_ES"])

class Command(BaseCommand):
    help = 'Crea una lliga amb equips, jugadors, partits i events'

    def add_arguments(self, parser):
        parser.add_argument('titol_lliga', nargs=1, type=str)

    def handle(self, *args, **options):
        titol_lliga = options['titol_lliga'][0]

        if Lliga.objects.filter(nom=titol_lliga).exists():
            print(f"Aquesta lliga ja està creada: {titol_lliga}")
            return

        # ---------- Crear la lliga ----------
        lliga = Lliga(nom=titol_lliga, temporada="2025/26")
        lliga.save()
        print(f"Lliga creada: {lliga}")

        # ---------- Crear equips ----------
        prefixos = ["RCD", "Athletic", "", "Deportivo", "Unión Deportiva"]
        equips = []

        for i in range(20):
            ciutat = faker.city()
            prefix = choice(prefixos)
            if prefix:
                prefix += " "
            nom_equip = f"{prefix}{ciutat}"
            equip = Equip(nom=nom_equip, ciutat=ciutat, lliga=lliga)
            equip.save()
            equips.append(equip)

            # ---------- Crear jugadors ----------
            for _ in range(25):
                jugador = Jugador(
                    nom=faker.name(),
                    posicio=choice(["porter", "defensa", "migcampista", "davanter"]),
                    edat=randint(18,35),
                    equip=equip
                )
                jugador.save()

        print(f"{len(equips)} equips i els seus jugadors creats.")

        # ---------- Crear partits ----------
        partits = []
        for local in equips:
            for visitant in equips:
                if local != visitant:
                    partit = Partit(local=local, visitant=visitant, lliga=lliga)
                    partit.inici = datetime.now() + timedelta(days=randint(0,30))
                    partit.save()
                    partits.append(partit)

                    # ---------- Crear events aleatoris (gols) ----------
                    num_gols_local = randint(0,5)
                    num_gols_visitant = randint(0,5)

                    for _ in range(num_gols_local):
                        Event.objects.create(
                            partit=partit,
                            temps=faker.time(),
                            tipus=Event.EventType.GOL,
                            equip=local,
                            jugador=choice(list(local.jugadors.all()))
                        )

                    for _ in range(num_gols_visitant):
                        Event.objects.create(
                            partit=partit,
                            temps=faker.time(),
                            tipus=Event.EventType.GOL,
                            equip=visitant,
                            jugador=choice(list(visitant.jugadors.all()))
                        )

        print(f"{len(partits)} partits creats amb events de gols.")
        print("Seeder completat!")