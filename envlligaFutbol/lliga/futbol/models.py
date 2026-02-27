from django.db import models

# --------- Lliga ---------
class Lliga(models.Model):
    nom = models.CharField(max_length=100)
    temporada = models.CharField(max_length=50, default="temporada")  # para poder usar en seeder y admin

    def __str__(self):
        return f"{self.nom} ({self.temporada})"


# --------- Equip ---------
class Equip(models.Model):
    nom = models.CharField(max_length=100)
    ciutat = models.CharField(max_length=100, blank=True, null=True)  # opcional, útil para seeder
    lliga = models.ForeignKey(Lliga, on_delete=models.CASCADE, related_name="equips")

    def __str__(self):
        return self.nom


# --------- Jugador ---------
class Jugador(models.Model):
    nom = models.CharField(max_length=100)
    posicio = models.CharField(max_length=50, blank=True, null=True)
    edat = models.IntegerField(blank=True, null=True)
    equip = models.ForeignKey(Equip, on_delete=models.CASCADE, related_name="jugadors")

    def __str__(self):
        return self.nom


# --------- Partit ---------
class Partit(models.Model):

    class Meta:
        unique_together = ["local", "visitant", "lliga"]

    local = models.ForeignKey(
        Equip,
        on_delete=models.CASCADE,
        related_name="partits_local"
    )
    visitant = models.ForeignKey(
        Equip,
        on_delete=models.CASCADE,
        related_name="partits_visitant"
    )
    lliga = models.ForeignKey(Lliga, on_delete=models.CASCADE, related_name="partits")
    detalls = models.TextField(null=True, blank=True)
    inici = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.local} - {self.visitant}"

    # Métodos para contar goles
    def gols_local(self):
        return self.event_set.filter(
            tipus=Event.EventType.GOL,
            equip=self.local
        ).count()

    def gols_visitant(self):
        return self.event_set.filter(
            tipus=Event.EventType.GOL,
            equip=self.visitant
        ).count()


# --------- Event ---------
class Event(models.Model):

    class EventType(models.TextChoices):
        GOL = "GOL"
        AUTOGOL = "AUTOGOL"
        FALTA = "FALTA"
        PENALTY = "PENALTY"
        MANS = "MANS"
        CESSIO = "CESSIO"
        FORA_DE_JOC = "FORA_DE_JOC"
        ASSISTENCIA = "ASSISTENCIA"
        TARGETA_GROGA = "TARGETA_GROGA"
        TARGETA_VERMELLA = "TARGETA_VERMELLA"

    partit = models.ForeignKey(Partit, on_delete=models.CASCADE)
    temps = models.TimeField()
    tipus = models.CharField(max_length=30, choices=EventType.choices)
    equip = models.ForeignKey(Equip, null=True, on_delete=models.SET_NULL)
    jugador = models.ForeignKey(
        Jugador,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events_fets"
    )
    jugador2 = models.ForeignKey(
        Jugador,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events_rebuts"
    )
    detalls = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.tipus} - {self.partit}"