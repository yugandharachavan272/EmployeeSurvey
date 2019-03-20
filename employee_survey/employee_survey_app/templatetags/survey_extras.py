# pylint: disable=invalid-name
# pylint: disable=broad-except
# pylint: disable=missing-docstring
# pylint: disable=no-member
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
from django import template

register = template.Library()


class CounterNode(template.Node):
    def __init__(self):
        self.count = 0

    def render(self, context):
        self.count += 1
        return self.count


@register.tag
def counter(parser, token):  # pylint: disable=unused-argument
    return CounterNode()
