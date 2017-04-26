from moderation import moderation
from moderation.db import ModeratedModel

from .models import *

# moderation.register(Roster)
moderation.register(FreeAgent)
