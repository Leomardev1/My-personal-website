import json

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe

register = template.Library()

# Impede que o texto feche a tag <script> ou seja interpretado como HTML.
_ESCAPES = {
    ord('<'): '\\u003C',
    ord('>'): '\\u003E',
    ord('&'): '\\u0026',
}


@register.simple_tag
def jsonld(dados):
    """Escreve um dicionário como dados estruturados (JSON-LD) para os motores de busca."""
    conteudo = json.dumps(dados, cls=DjangoJSONEncoder, ensure_ascii=False).translate(_ESCAPES)
    return mark_safe(f'<script type="application/ld+json">{conteudo}</script>')
