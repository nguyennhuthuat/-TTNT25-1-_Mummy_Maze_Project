import pygame
import os
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT
from .utils import Button


class HighScoresScreen:
    """High Scores screen displaying top 5 players with ranks"""

    # Default high scores data (rank 1-4 are fixed, rank 5 is for current player if < 24057)
    DEFAULT_HIGH_SCORES = [
        {"username": "thachdz", "score": 44920},
        {"username": "Ithebest", "score": 42108},
        {"username": "co102", "score": 35005},
        {"username": "thuatga", "score": 24057},
    ]

    def __init__(self, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_open = False
        self.current_player_score = 0
        self.current_player_name = ""

        # Paths
        self.bg_path = os.path.join("Assets", "images", "banghighscores.png")
        self.font_path = os.path.join("Assets", "Fonts", "VT323-Regular.ttf")

        # Load background
        try:
            self.background = pygame.image.load(self.bg_path).convert_alpha()
            bg_w, bg_h = self.background.get_size()
            target_h = min(550, screen_height - 60)
            if bg_h > target_h:
                scale_ratio = target_h / bg_h
                new_w = int(bg_w * scale_ratio)
                new_h = int(bg_h * scale_ratio)
                self.background = pygame.transform.smoothscale(
                    self.background, (new_w, new_h)
                )
        except:
            print(f"Could not load {self.bg_path}")
            self.background = pygame.Surface((500, 450))
            self.background.fill((194, 154, 108))

        self.bg_rect = self.background.get_rect(
            center=(screen_width // 2, screen_height // 2)
        )

        # Load fonts
        try:
            self.title_font = pygame.font.Font(self.font_path, 40)
            self.header_font = pygame.font.Font(self.font_path, 36)
            self.score_font = pygame.font.Font(self.font_path, 38)
        except:
            print(f"Could not load font {self.font_path}")
            self.title_font = pygame.font.Font(None, 40)
            self.header_font = pygame.font.Font(None, 36)
            self.score_font = pygame.font.Font(None, 38)

        # Colors
        self.text_color = (60, 80, 60)  # Dark green/olive color for text
        self.highlight_color = (
            139,
            69,
            19,
        )  # Saddle brown for highlighting current player

    def set_current_player(self, name, score):
        """Set the current player's name and score"""
        self.current_player_name = name
        self.current_player_score = score

    def get_ranked_scores(self):
        """
        Get the ranked scores list with current player inserted if applicable.
        Returns list of 5 entries with rank, username, score.
        Rank 5 is always the current player ("You") with their current score.
        If current player's score is high enough, they move up in rank and push others down.
        """
        # Start with default scores (only top 4)
        scores = [s.copy() for s in self.DEFAULT_HIGH_SCORES]

        # Create result list with 5 ranks
        result = []

        # Check where current player should be inserted based on score
        player_rank = 4  # Default to rank 5 (index 4)

        if self.current_player_score > 0:
            # Find position for current player
            for i, entry in enumerate(scores):
                if self.current_player_score > entry["score"]:
                    player_rank = i
                    break

        # Build the ranked list
        scores_index = 0
        for i in range(5):
            if i == player_rank:
                # This is the current player's position
                result.append(
                    {
                        "rank": i + 1,
                        "username": "You",
                        "score": self.current_player_score,
                        "is_current_player": True,
                    }
                )
            else:
                if scores_index < len(scores):
                    entry = scores[scores_index]
                    result.append(
                        {
                            "rank": i + 1,
                            "username": entry["username"],
                            "score": entry["score"],
                            "is_current_player": False,
                        }
                    )
                    scores_index += 1
                else:
                    # Empty rank (shouldn't happen with 4 default scores + 1 player)
                    result.append(
                        {
                            "rank": i + 1,
                            "username": "",
                            "score": 0,
                            "is_current_player": False,
                        }
                    )

        return result[:5]  # Only return top 5

    def handle_event(self, event):
        """Handle events for the high scores screen"""
        if not self.is_open:
            return None

        # Close on click or key press
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_open = False
            return "CLOSE_HIGH_SCORES"

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                self.is_open = False
                return "CLOSE_HIGH_SCORES"

        return None

    def draw(self, screen):
        """Draw the high scores screen"""
        if not self.is_open:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        # Draw background
        screen.blit(self.background, self.bg_rect)

        # Get ranked scores
        ranked_scores = self.get_ranked_scores()

        # Calculate positions for the table
        # Header row
        header_y = self.bg_rect.top + int(self.bg_rect.height * 0.18)

        # Column positions (relative to background)
        rank_x = self.bg_rect.left + int(self.bg_rect.width * 0.12)
        username_x = self.bg_rect.left + int(self.bg_rect.width * 0.38)
        score_x = self.bg_rect.left + int(self.bg_rect.width * 0.72)

        # Draw header row
        rank_header = self.header_font.render("Rank", True, self.text_color)
        username_header = self.header_font.render("Username", True, self.text_color)
        score_header = self.header_font.render("Score", True, self.text_color)

        screen.blit(rank_header, (rank_x - rank_header.get_width() // 2, header_y))
        screen.blit(
            username_header, (username_x - username_header.get_width() // 2, header_y)
        )
        screen.blit(score_header, (score_x - score_header.get_width() // 2, header_y))

        # Draw score rows
        row_height = int(self.bg_rect.height * 0.13)
        start_y = header_y + row_height

        for i, entry in enumerate(ranked_scores):
            y = start_y + i * row_height

            # Choose color based on whether this is the current player
            color = (
                self.highlight_color if entry["is_current_player"] else self.text_color
            )

            # Draw rank
            rank_text = self.score_font.render(str(entry["rank"]), True, color)
            screen.blit(rank_text, (rank_x - rank_text.get_width() // 2, y))

            # Draw username
            if entry["username"]:
                username_text = self.score_font.render(entry["username"], True, color)
                screen.blit(
                    username_text, (username_x - username_text.get_width() // 2, y)
                )

            # Draw score
            if entry["score"] > 0:
                score_text = self.score_font.render(str(entry["score"]), True, color)
                screen.blit(score_text, (score_x - score_text.get_width() // 2, y))


class OptionsMenu:
    def __init__(self, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_open = False

        # Initialize High Scores Screen
        self.high_scores_screen = HighScoresScreen(screen_width, screen_height)

        # Paths relative to the execution context or absolute
        self.bg_path = os.path.join("Assets", "images", "bangoption.png")
        self.btn_img_path = os.path.join("Assets", "images", "buttonoption.png")
        self.font_path = os.path.join("Assets", "Fonts", "VT323-Regular.ttf")

        # Load background
        try:
            self.background = pygame.image.load(self.bg_path).convert_alpha()
            # Scale background to fit screen reasonably (e.g. max height 550)
            bg_w, bg_h = self.background.get_size()
            target_h = min(550, screen_height - 60)
            if bg_h > target_h:
                scale_ratio = target_h / bg_h
                new_w = int(bg_w * scale_ratio)
                new_h = int(bg_h * scale_ratio)
                self.background = pygame.transform.smoothscale(
                    self.background, (new_w, new_h)
                )
        except:
            print(f"Could not load {self.bg_path}")
            self.background = pygame.Surface((400, 500))
            self.background.fill((50, 50, 50))

        self.bg_rect = self.background.get_rect(
            center=(screen_width // 2, screen_height // 2)
        )

        # Load Font
        try:
            self.font = pygame.font.Font(self.font_path, 30)
        except:
            print(f"Could not load font {self.font_path}")
            self.font = pygame.font.Font(None, 30)

        # Create Buttons
        self.buttons = []
        labels = ["Back To The Previous Level", "High Scores", "Tutorial", "Done"]

        # Calculate positions
        # Center buttons vertically in the available space below the "title" area of the background
        # Assuming top 15% is title/header
        area_top = self.bg_rect.top + int(self.bg_rect.height * 0.15)
        area_height = self.bg_rect.height * 0.85

        btn_height = 40  # Slightly smaller to fit
        gap = 10
        total_btn_h = len(labels) * btn_height + (len(labels) - 1) * gap

        start_y = area_top + (area_height - total_btn_h) // 2

        # Calculate max text width to ensure all text fits
        max_text_w = 0
        for label in labels:
            w = self.font.size(label)[0]
            max_text_w = max(max_text_w, w)

        btn_width = max_text_w + 60  # Add padding

        center_x = self.bg_rect.centerx

        for i, label in enumerate(labels):
            y = start_y + i * (btn_height + gap)
            x = center_x - btn_width // 2

            # Using Utils Button
            btn = Button(
                x,
                y,
                btn_width,
                btn_height,
                text="",
                image_path=self.btn_img_path,
                keep_aspect_ratio=False,
            )
            self.buttons.append({"btn": btn, "label": label})

    def set_current_player(self, name, score):
        """Set the current player's name and score for high scores display"""
        self.high_scores_screen.set_current_player(name, score)

    def handle_event(self, event):
        if not self.is_open:
            return None

        # Handle high scores screen events first if it's open
        if self.high_scores_screen.is_open:
            hs_action = self.high_scores_screen.handle_event(event)
            if hs_action == "CLOSE_HIGH_SCORES":
                return None  # Stay in options menu
            return None  # Block other events while high scores is open

        action = None
        for item in self.buttons:
            btn = item["btn"]
            label = item["label"]

            # Init hover check manually if not done in event loop
            if event.type == pygame.MOUSEMOTION:
                btn.check_hover(event.pos)

            if btn.is_clicked(event):
                action = label

        if action == "Done":
            self.is_open = False
            return "DONE_MENU"  # Return special code or just close

        if action == "High Scores":
            self.high_scores_screen.is_open = True
            return None  # Don't return action, handle internally
    

        return action

    def draw(self, screen):
        if not self.is_open:
            return

        # Semi-transparent overlay behind the menu
        overlay = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        screen.blit(self.background, self.bg_rect)

        for item in self.buttons:
            btn = item["btn"]
            label = item["label"]

            # Draw button image
            btn.draw(screen)

            # Draw text centered on button
            text_surf = self.font.render(label, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=btn.rect.center)
            screen.blit(text_surf, text_rect)

        # Draw high scores screen on top if open
        if self.high_scores_screen.is_open:
            self.high_scores_screen.draw(screen)
