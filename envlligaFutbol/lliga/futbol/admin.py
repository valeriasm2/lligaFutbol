from django.contrib import admin
from .models import Partit, Event, Lliga, Equip, Jugador

admin.site.register(Lliga)
admin.site.register(Equip)
admin.site.register(Jugador)

class EventInline(admin.TabularInline):
    model = Event
    fields = ["temps", "tipus", "jugador", "equip"]
    ordering = ("temps",)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if request.resolver_match.kwargs.get("object_id"):
            partit_id = request.resolver_match.kwargs.get("object_id")
            partit = Partit.objects.get(pk=partit_id)
            if db_field.name == "jugador":
                kwargs["queryset"] = Jugador.objects.filter(
                    equip__in=[partit.local, partit.visitant]
                )
            if db_field.name == "equip":
                kwargs["queryset"] = Equip.objects.filter(
                    id__in=[partit.local.id, partit.visitant.id]
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Partit)
class PartitAdmin(admin.ModelAdmin):
    search_fields = ["local__nom", "visitant__nom", "lliga__nom"]
    readonly_fields = ["resultat"]
    list_display = ["local", "visitant", "resultat", "lliga", "inici"]
    ordering = ("-inici",)
    inlines = [EventInline]

    def resultat(self, obj):
        gols_local = obj.event_set.filter(tipus=Event.EventType.GOL, equip=obj.local).count()
        gols_visit = obj.event_set.filter(tipus=Event.EventType.GOL, equip=obj.visitant).count()
        return "{} - {}".format(gols_local, gols_visit)
    resultat.short_description = "Resultat"

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["partit", "tipus", "equip", "jugador", "temps"]