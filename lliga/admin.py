from django.contrib import admin
from .models import Lliga, Equip, Jugador, Partit, Event


@admin.register(Lliga)
class LligaAdmin(admin.ModelAdmin):
    list_display = ["titol", "temporada"]
    search_fields = ["titol"]


@admin.register(Equip)
class EquipAdmin(admin.ModelAdmin):
    list_display = ["nom", "lliga", "ciutat"]
    list_filter = ["lliga"]
    search_fields = ["nom"]


@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = ["dorsal", "nom", "cognom", "equip", "posicio"]
    list_filter = ["equip__lliga", "equip"]
    search_fields = ["nom", "cognom"]
    ordering = ["equip", "dorsal"]


class EventInline(admin.TabularInline):
    model = Event
    fields = ["temps", "tipus", "jugador", "equip"]
    ordering = ("temps",)
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # filtrem els jugadors i només deixem els que siguin d'algun dels 2 equips (local o visitant)
        if db_field.name == "jugador":
            partit_id = request.resolver_match.kwargs.get('object_id')
            if partit_id:
                partit = Partit.objects.get(id=partit_id)
                # fem un queryset per cada equip
                jugadors_locals = Jugador.objects.filter(equip=partit.local)
                jugadors_visitants = Jugador.objects.filter(equip=partit.visitant)
                # fusionem els 2 querysets amb l'operador | (= union en BD)
                kwargs["queryset"] = jugadors_locals | jugadors_visitants
        if db_field.name == "equip":
            partit_id = request.resolver_match.kwargs.get('object_id')
            if partit_id:
                partit = Partit.objects.get(id=partit_id)
                kwargs["queryset"] = Equip.objects.filter(
                    id__in=[partit.local.id, partit.visitant.id]
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class PartitAdmin(admin.ModelAdmin):
    # Cerca per nom d'equips o títol de lliga
    search_fields = ["local__nom", "visitant__nom", "lliga__titol"]
    # El resultat és camp calculat, no editable
    readonly_fields = ["resultat"]
    # Llista: local, visitant, resultat, lliga i data
    list_display = ["local", "visitant", "resultat", "lliga", "inici"]
    list_filter = ["lliga"]
    ordering = ("-inici",)
    inlines = [EventInline]

    def resultat(self, obj):
        gols_local = obj.event_set.filter(
            tipus=Event.EventType.GOL, equip=obj.local
        ).count()
        gols_visit = obj.event_set.filter(
            tipus=Event.EventType.GOL, equip=obj.visitant
        ).count()
        return "{} - {}".format(gols_local, gols_visit)


admin.site.register(Partit, PartitAdmin)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    # Llista: (local+visitant via partit), tipus, equip, jugador, temps
    list_display = ["partit", "tipus", "equip", "jugador", "temps"]
    list_filter = ["tipus", "equip__lliga"]
    ordering = ["partit", "temps"]
