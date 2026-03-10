from django.db import models


class Lliga(models.Model):
    titol = models.CharField(max_length=100)
    temporada = models.CharField(max_length=20, default="2024-25")

    def __str__(self):
        return f"{self.titol} ({self.temporada})"


class Equip(models.Model):
    nom = models.CharField(max_length=100)
    lliga = models.ForeignKey(Lliga, on_delete=models.CASCADE)
    ciutat = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.nom


class Jugador(models.Model):
    nom = models.CharField(max_length=100)
    cognom = models.CharField(max_length=100)
    dorsal = models.IntegerField()
    equip = models.ForeignKey(Equip, on_delete=models.CASCADE)
    posicio = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.dorsal}. {self.nom} {self.cognom} ({self.equip})"


class Partit(models.Model):
    class Meta:
        unique_together = ["local", "visitant", "lliga"]

    local = models.ForeignKey(Equip, on_delete=models.CASCADE, related_name="partits_local")
    visitant = models.ForeignKey(Equip, on_delete=models.CASCADE, related_name="partits_visitant")
    lliga = models.ForeignKey(Lliga, on_delete=models.CASCADE)
    detalls = models.TextField(null=True, blank=True)
    inici = models.DateTimeField(null=True, blank=True)
    jornada = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.local} - {self.visitant}"

    def gols_local(self):
        return self.event_set.filter(tipus=Event.EventType.GOL, equip=self.local).count()

    def gols_visitant(self):
        return self.event_set.filter(tipus=Event.EventType.GOL, equip=self.visitant).count()

    def resultat(self):
        return f"{self.gols_local()} - {self.gols_visitant()}"


class Event(models.Model):
    class EventType(models.TextChoices):
        GOL = "GOL", "⚽ Gol"
        AUTOGOL = "AUTOGOL", "🙈 Autogol"
        FALTA = "FALTA", "⚠️ Falta"
        PENALTY = "PENALTY", "🎯 Penalti"
        TARGETA_GROGA = "TARGETA_GROGA", "🟨 Targeta groga"
        TARGETA_VERMELLA = "TARGETA_VERMELLA", "🟥 Targeta vermella"
        ASSISTENCIA = "ASSISTENCIA", "👟 Assistència"

    partit = models.ForeignKey(Partit, on_delete=models.CASCADE)
    temps = models.TimeField()
    tipus = models.CharField(max_length=30, choices=EventType.choices)
    jugador = models.ForeignKey(Jugador, null=True, on_delete=models.SET_NULL, related_name="events_fets")
    equip = models.ForeignKey(Equip, null=True, on_delete=models.SET_NULL)
    jugador2 = models.ForeignKey(Jugador, null=True, blank=True, on_delete=models.SET_NULL, related_name="events_rebuts")
    detalls = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.temps} - {self.tipus} - {self.jugador}"
