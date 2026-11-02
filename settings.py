"""Option lists, tuning tables and UI strings (no Kivy imports: unit-testable)."""

OPTIONS = {
    'control': ['touch', 'tilt', 'both'],
    'sensitivity': ['Low', 'Medium', 'High'],
    'quality': ['Low', 'Medium', 'High'],
    'language': ['English', 'Español', 'Français'],
}

CONTROL_LABEL = {'touch': 'Touch / Swipe', 'tilt': 'Phone Tilt', 'both': 'Both'}

# fraction of screen width a finger must travel to count as a swipe
SWIPE_FRAC = {'Low': 0.11, 'Medium': 0.07, 'High': 0.045}
# tilt tuning in m/s^2 of lateral gravity component (about 10 deg = 1.7)
TILT_THRESH = {'Low': 3.0, 'Medium': 2.0, 'High': 1.3}
TILT_DEAD = {'Low': 1.3, 'Medium': 0.9, 'High': 0.6}

STR = {
    'English': {
        'play': 'PLAY', 'character': 'CHARACTER', 'settings': 'SETTINGS',
        'high_score': 'HIGH SCORE', 'quit': 'QUIT', 'paused': 'PAUSED',
        'resume': 'RESUME', 'restart': 'RESTART', 'home': 'HOME', 'next': 'NEXT',
        'back': 'BACK', 'select': 'SELECT', 'unlock': 'UNLOCK', 'selected': 'SELECTED',
        'previous': 'PREV', 'music': 'Music', 'sfx': 'Sound Effects',
        'graphics': 'Graphics Quality', 'control_style': 'Control Style',
        'language': 'Language', 'sensitivity': 'Sensitivity',
        'calibrate': 'CALIBRATE NOW', 'calibrated': 'Calibrated!',
        'no_sensor': 'No accelerometer found', 'sensor_ok': 'Accelerometer detected',
        'level_complete': 'LEVEL COMPLETE!', 'game_over': 'GAME OVER',
        'score': 'Score', 'coins': 'Coins', 'distance': 'Distance', 'best': 'Best',
        'speed': 'Speed', 'health': 'Health', 'magnet': 'Magnet', 'locked': 'LOCKED',
        'character_select': 'CHARACTER SELECT', 'achievements': 'ACHIEVEMENTS',
        'tilt_sensor': 'Tilt', 'press_back_again': 'Press back again to quit',
        'tagline': 'Run • Jump • Survive\nBe The Legend...',
        'subtitle': 'ENDLESS ADVENTURE', 'level': 'Level', 'need_coins': 'Not enough coins',
    },
    'Español': {
        'play': 'JUGAR', 'character': 'PERSONAJE', 'settings': 'AJUSTES',
        'high_score': 'RÉCORD', 'quit': 'SALIR', 'paused': 'PAUSA',
        'resume': 'SEGUIR', 'restart': 'REINICIAR', 'home': 'INICIO', 'next': 'SIGUIENTE',
        'back': 'ATRÁS', 'select': 'ELEGIR', 'unlock': 'DESBLOQUEAR', 'selected': 'ELEGIDO',
        'previous': 'ANT.', 'music': 'Música', 'sfx': 'Efectos de sonido',
        'graphics': 'Calidad gráfica', 'control_style': 'Control',
        'language': 'Idioma', 'sensitivity': 'Sensibilidad',
        'calibrate': 'CALIBRAR AHORA', 'calibrated': '¡Calibrado!',
        'no_sensor': 'Sin acelerómetro', 'sensor_ok': 'Acelerómetro detectado',
        'level_complete': '¡NIVEL COMPLETO!', 'game_over': 'FIN DEL JUEGO',
        'score': 'Puntos', 'coins': 'Monedas', 'distance': 'Distancia', 'best': 'Mejor',
        'speed': 'Velocidad', 'health': 'Salud', 'magnet': 'Imán', 'locked': 'BLOQUEADO',
        'character_select': 'ELEGIR PERSONAJE', 'achievements': 'LOGROS',
        'tilt_sensor': 'Inclinación', 'press_back_again': 'Pulsa atrás otra vez para salir',
        'tagline': 'Corre • Salta • Sobrevive\nSé la leyenda...',
        'subtitle': 'AVENTURA INFINITA', 'level': 'Nivel', 'need_coins': 'Faltan monedas',
    },
    'Français': {
        'play': 'JOUER', 'character': 'PERSONNAGE', 'settings': 'RÉGLAGES',
        'high_score': 'MEILLEUR SCORE', 'quit': 'QUITTER', 'paused': 'PAUSE',
        'resume': 'REPRENDRE', 'restart': 'REJOUER', 'home': 'ACCUEIL', 'next': 'SUIVANT',
        'back': 'RETOUR', 'select': 'CHOISIR', 'unlock': 'DÉBLOQUER', 'selected': 'CHOISI',
        'previous': 'PRÉC.', 'music': 'Musique', 'sfx': 'Effets sonores',
        'graphics': 'Qualité graphique', 'control_style': 'Contrôle',
        'language': 'Langue', 'sensitivity': 'Sensibilité',
        'calibrate': 'CALIBRER', 'calibrated': 'Calibré !',
        'no_sensor': "Pas d'accéléromètre", 'sensor_ok': 'Accéléromètre détecté',
        'level_complete': 'NIVEAU TERMINÉ !', 'game_over': 'PARTIE TERMINÉE',
        'score': 'Score', 'coins': 'Pièces', 'distance': 'Distance', 'best': 'Record',
        'speed': 'Vitesse', 'health': 'Santé', 'magnet': 'Aimant', 'locked': 'VERROUILLÉ',
        'character_select': 'CHOIX DU PERSONNAGE', 'achievements': 'SUCCÈS',
        'tilt_sensor': 'Inclinaison', 'press_back_again': 'Appuyez encore sur retour pour quitter',
        'tagline': 'Cours • Saute • Survis\nSois la légende...',
        'subtitle': 'AVENTURE SANS FIN', 'level': 'Niveau', 'need_coins': 'Pas assez de pièces',
    },
}


def tr(lang, key):
    table = STR.get(lang) or STR['English']
    return table.get(key) or STR['English'].get(key, key)


def cycle(save, key, step=1):
    """Cycle a saved option through OPTIONS[key] and persist it."""
    lst = OPTIONS[key]
    try:
        i = lst.index(save[key])
    except ValueError:
        i = 0
    save[key] = lst[(i + step) % len(lst)]
    save.save()
    return save[key]
