from questionary import Style

color_azul = "#4040f0"
color_amarillo = "#ffdf30"
color_blanco = "#ffffff"
color_verde = "#40ff40"
color_gris = "#858585"

custom_style_fancy = Style(
    [
        ("qmark", "fg:#673ab7 bold"),  # token in front of the question
        ("question", f"fg:{color_blanco} bold"),  # question text
        (
            "answer",
            f"fg:{color_amarillo} bold",
        ),  # submitted answer text behind the question
        (
            "pointer",
            f"fg:{color_azul} bold",
        ),  # pointer used in select and checkbox prompts
        (
            "highlighted",
            f"fg:{color_azul} bold",
        ),  # pointed-at choice in select and checkbox prompts
        ("selected", f"fg:{color_verde}"),  # style for a selected item of a checkbox
        ("separator", f"fg:{color_verde}"),  # separator in lists
        ("instruction", ""),  # user instructions for select, rawselect, checkbox
        ("text", f"fg:{color_gris} italic"),  # plain text
        (
            "disabled",
            "fg:#858585 italic",
        ),  # disabled choices for select and checkbox prompts
    ]
)
