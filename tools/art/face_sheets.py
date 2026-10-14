"""Which portrait sits where on the face sheets (img/faces/*.png).

Shared by the art build (faces.py draws them) and the data build (dialogue
picks a portrait by speaker), so it has no dependencies of its own.
"""

# face sheet name -> sprite names in face-index order
SHEETS = {
    'YY_Yin': ['$Yin_Child', '$Yin_Teen', '$Yin_Adult', '$Yin_Middle', '$Yin_Old'],
    'YY_Family': ['$Grandpa', '$Mom', '$Jie_Teen', '$Jie_Adult', '$Jie_Old', '$Duoduo',
                  '$Teacher_Wang', '$Cafe_Owner'],
    'YY_Friends': ['$Xiaoyu_Child', '$Xiaoyu_Adult', '$Xiaohe_Child', '$Xiaohe_Adult', '$Xiaoyu_Mom',
                   '$Receptionist'],
    'YY_Village': ['$Granny_Li', '$Farmer', '$Fisherman', '$Vendor', '$Villager_Woman', '$Kid_Boy',
                   '$Kid_Girl'],
}


def face_index(sprite):
    """sprite name -> (face sheet, index)"""
    for sheet, names in SHEETS.items():
        if sprite in names:
            return sheet, names.index(sprite)
    raise KeyError(sprite)
