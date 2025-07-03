from backend.text_adventure_games.actions.base import Action

class Legend(Action):
    ACTION_NAME = "legend"
    ACTION_DESCRIPTION = "Show item-specific hints and available actions."
    ACTION_ALIASES = []

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)

    def check_preconditions(self) -> bool:
        return True

    def apply_effects(self):
        hints = get_item_hints(self.game)
        actions = self.game.parser.get_available_actions(self.character)
        legend_lines = []
        if hints:
            legend_lines.append("Item-specific hints:")
            legend_lines.extend(hints)
        legend_lines.append("Available actions:")
        for act in actions:
            cmd = act.get('command', '')
            desc = act.get('description', '')
            if desc:
                legend_lines.append(f"  {cmd:16} - {desc[:50]}")
            else:
                legend_lines.append(f"  {cmd}")
        return self.parser.ok("\n".join(legend_lines))

def get_item_hints(game_obj):
    hints = []
    location = game_obj.player.location
    for item in getattr(location, 'items', {}).values():
        # Bed legend (special case)
        if getattr(item, 'name', '').lower() == 'bed':
            try:
                from backend.text.house_actions.bed import get_bed_legend
                hints.append(get_bed_legend())
            except Exception:
                pass
        # General command hints
        for cmd in getattr(item, 'get_command_hints', lambda: [])():
            hints.append(f"  {cmd}")
    return hints 