from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from .models import Lliga, Equip, Jugador, Partit, Event


def index(request):
    lligues = Lliga.objects.all()
    return render(request, 'lliga/index.html', {'lligues': lligues})


def partits(request, lliga_id):
    lliga = get_object_or_404(Lliga, id=lliga_id)
    llista = Partit.objects.filter(lliga=lliga).order_by('inici')
    return render(request, 'lliga/partits.html', {'lliga': lliga, 'partits': llista})


def partit_detall(request, partit_id):
    partit = get_object_or_404(Partit, id=partit_id)
    events = partit.event_set.order_by('temps')
    return render(request, 'lliga/partit_detall.html', {'partit': partit, 'events': events})


def classificacio(request, lliga_id):
    lliga = get_object_or_404(Lliga, id=lliga_id)
    equips = Equip.objects.filter(lliga=lliga)
    taula = []
    for equip in equips:
        partits_jugats = Partit.objects.filter(
            Q(local=equip) | Q(visitant=equip), lliga=lliga, inici__isnull=False
        )
        punts = pg = pe = pp = gf = gc = 0
        for p in partits_jugats:
            gl = p.gols_local()
            gv = p.gols_visitant()
            if equip == p.local:
                gf += gl; gc += gv
                if gl > gv: punts += 3; pg += 1
                elif gl == gv: punts += 1; pe += 1
                else: pp += 1
            else:
                gf += gv; gc += gl
                if gv > gl: punts += 3; pg += 1
                elif gl == gv: punts += 1; pe += 1
                else: pp += 1
        taula.append({
            'equip': equip, 'pj': pg+pe+pp,
            'pg': pg, 'pe': pe, 'pp': pp,
            'gf': gf, 'gc': gc, 'dg': gf-gc, 'punts': punts,
        })
    taula.sort(key=lambda x: (-x['punts'], -x['dg'], -x['gf']))
    return render(request, 'lliga/classificacio.html', {'lliga': lliga, 'taula': taula})


def pichichi(request, lliga_id):
    lliga = get_object_or_404(Lliga, id=lliga_id)
    golejadors = Jugador.objects.filter(
        equip__lliga=lliga,
        events_fets__tipus=Event.EventType.GOL
    ).annotate(
        gols=Count('events_fets', filter=Q(events_fets__tipus=Event.EventType.GOL))
    ).order_by('-gols')
    return render(request, 'lliga/pichichi.html', {'lliga': lliga, 'golejadors': golejadors})
