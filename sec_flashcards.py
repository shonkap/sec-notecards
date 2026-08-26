import glob
import json
import os
import random
import tkinter as tk
from tkinter import ttk


class FlashcardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Security+ Study Deck")
        self.geometry("760x620")
        self.minsize(680, 540)
        self.configure(bg="#101821")

        self.cards_directory = "cards"
        self.all_cards = []
        self.active_cards = []
        self.current_index = 0
        self.flip_state = 0

        self.load_cards_from_folder()
        self.setup_ui()
        self.bind_shortcuts()
        self.reset_filter()

    def load_cards_from_folder(self):
        if not os.path.exists(self.cards_directory):
            os.makedirs(self.cards_directory)

        self.categories = ["All Categories"]
        self.all_cards = []

        json_files = glob.glob(os.path.join(self.cards_directory, "*.json"))
        for filepath in json_files:
            category_name = os.path.basename(filepath).replace(".json", "").replace("_", " ").title()
            self.categories.append(category_name)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        self.all_cards.append((category_name, item))
            except Exception as e:
                print(f"Error loading {filepath}: {e}")

    def setup_ui(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#101821")
        self.style.configure("TLabel", background="#101821", foreground="#EAF2FF")
        self.style.configure("TEntry", fieldbackground="#1B2733", foreground="#EAF2FF", padding=6)
        self.style.configure(
            "TCombobox",
            fieldbackground="#1B2733",
            foreground="#EAF2FF",
            padding=6,
            arrowcolor="#7DC4FF",
            borderwidth=1,
            relief="solid",
        )
        self.style.map(
            "TCombobox",
            fieldbackground=[("readonly", "#1B2733"), ("!readonly", "#1B2733")],
            foreground=[("readonly", "#EAF2FF"), ("!readonly", "#EAF2FF")],
            background=[("readonly", "#1B2733"), ("!readonly", "#1B2733")],
        )

        self.style.configure(
            "Primary.TButton",
            background="#6EA8FE",
            foreground="#08131E",
            borderwidth=1,
            padding=(16, 8),
            relief="flat",
            font=("Segoe UI", 10, "bold"),
        )
        self.style.configure(
            "Secondary.TButton",
            background="#243549",
            foreground="#EAF2FF",
            borderwidth=1,
            padding=(16, 8),
            relief="flat",
            font=("Segoe UI", 10, "bold"),
        )
        self.style.map(
            "Primary.TButton",
            background=[("pressed", "#4C8DFF"), ("active", "#8CB8FF")],
            foreground=[("pressed", "#08131E"), ("active", "#08131E")],
            relief=[("pressed", "flat"), ("active", "flat")],
        )
        self.style.map(
            "Secondary.TButton",
            background=[("pressed", "#324B67"), ("active", "#2F4158")],
            foreground=[("pressed", "#FFFFFF"), ("active", "#FFFFFF")],
            relief=[("pressed", "flat"), ("active", "flat")],
        )

        header_frame = tk.Frame(self, bg="#101821")
        header_frame.pack(fill="x", padx=18, pady=(16, 8))

        title_label = tk.Label(
            header_frame,
            text="Security+ Study Deck",
            bg="#101821",
            fg="#F5F9FF",
            font=("Segoe UI", 24, "bold"),
            anchor="w",
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            header_frame,
            text="Quick review for key terms, protocols, and functions",
            bg="#101821",
            fg="#9DB2C9",
            font=("Segoe UI", 11),
            anchor="w",
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))

        controls_frame = tk.LabelFrame(
            self,
            text=" Study Controls ",
            bg="#1B2430",
            fg="#EAF2FF",
            bd=1,
            relief="solid",
            font=("Segoe UI", 10, "bold"),
        )
        controls_frame.pack(fill="x", padx=16, pady=(0, 10))

        controls_frame.columnconfigure(1, weight=1)
        controls_frame.columnconfigure(3, weight=1)

        ttk.Label(controls_frame, text="Category:", background="#1B2430").grid(row=0, column=0, sticky="w", padx=(12, 6), pady=(10, 6))
        self.cat_var = tk.StringVar(value="All Categories")
        self.cat_dropdown = ttk.Combobox(controls_frame, textvariable=self.cat_var, values=self.categories, state="readonly", width=36)
        self.cat_dropdown.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=(10, 6))
        self.cat_dropdown.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        ttk.Label(controls_frame, text="Search:", background="#1B2430").grid(row=0, column=2, sticky="w", padx=(0, 6), pady=(10, 6))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(controls_frame, textvariable=self.search_var, width=20)
        self.search_entry.grid(row=0, column=3, sticky="ew", padx=(0, 12), pady=(10, 6))
        self.search_entry.bind("<KeyRelease>", lambda e: self.apply_filters())

        ttk.Label(controls_frame, text="Start View:", background="#1B2430").grid(row=1, column=0, sticky="w", padx=(12, 6), pady=(4, 12))
        self.start_view_var = tk.StringVar(value="Term / Port")
        self.start_view_dropdown = ttk.Combobox(
            controls_frame,
            textvariable=self.start_view_var,
            values=["Term / Port", "Protocol", "Description"],
            state="readonly",
            width=18,
        )
        self.start_view_dropdown.grid(row=1, column=1, sticky="w", padx=(0, 12), pady=(4, 12))
        self.start_view_dropdown.bind("<<ComboboxSelected>>", lambda e: self.on_start_view_change())

        btn_frame = ttk.Frame(controls_frame)
        btn_frame.grid(row=1, column=2, columnspan=2, sticky="e", padx=(0, 12), pady=(4, 12))
        ttk.Button(btn_frame, text="🔀 Randomize (R)", style="Secondary.TButton", command=self.shuffle_current).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="🔄 Reset", style="Secondary.TButton", command=self.reset_filter).pack(side="left")

        self.card_frame = tk.Frame(self, bg="#1C2A38", highlightbackground="#40516A", highlightthickness=2)
        self.card_frame.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        self.card_frame.bind("<Button-1>", lambda e: self.flip_card())

        self.category_label = tk.Label(
            self.card_frame,
            text="",
            fg="#A9BFD6",
            bg="#1C2A38",
            font=("Segoe UI", 10, "italic"),
            anchor="w",
        )
        self.category_label.pack(anchor="nw", padx=18, pady=(14, 6))
        self.category_label.bind("<Button-1>", lambda e: self.flip_card())

        self.card_title = tk.Label(
            self.card_frame,
            text="",
            fg="#8DD1FF",
            bg="#1C2A38",
            font=("Segoe UI", 11, "bold"),
            anchor="center",
        )
        self.card_title.pack(fill="x", padx=18, pady=(0, 2))
        self.card_title.bind("<Button-1>", lambda e: self.flip_card())

        self.card_text = tk.Label(
            self.card_frame,
            text="",
            fg="#FFFFFF",
            bg="#1C2A38",
            font=("Segoe UI", 22, "bold"),
            wraplength=630,
            justify="center",
            padx=18,
            pady=22,
        )
        self.card_text.pack(expand=True, fill="both", padx=18)
        self.card_text.bind("<Button-1>", lambda e: self.flip_card())

        self.flip_hint = tk.Label(
            self.card_frame,
            text="Press Space or click the card to flip",
            fg="#8EA7C0",
            bg="#1C2A38",
            font=("Segoe UI", 10),
        )
        self.flip_hint.pack(anchor="s", pady=(6, 14))
        self.flip_hint.bind("<Button-1>", lambda e: self.flip_card())

        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill="x", padx=16, pady=(0, 14))

        ttk.Button(nav_frame, text="◀ Previous", style="Secondary.TButton", command=self.prev_card).pack(side="left")
        self.counter_label = ttk.Label(nav_frame, text="0 / 0", foreground="#EAF2FF", background="#101821", font=("Segoe UI", 10, "bold"))
        self.counter_label.pack(side="left", expand=True)
        ttk.Button(nav_frame, text="Next ▶", style="Secondary.TButton", command=self.next_card).pack(side="right")

    def bind_shortcuts(self):
        self.bind("<space>", lambda e: self.flip_card())
        self.bind("<Right>", lambda e: self.next_card())
        self.bind("<Left>", lambda e: self.prev_card())
        self.bind("<Down>", lambda e: self.next_card())
        self.bind("<Up>", lambda e: self.prev_card())
        self.bind("<r>", lambda e: self.shuffle_current())
        self.bind("<R>", lambda e: self.shuffle_current())

    def get_initial_flip_state(self):
        selection = self.start_view_var.get()
        if selection == "Protocol":
            return 1
        if selection == "Description":
            return 2
        return 0

    def on_start_view_change(self):
        self.flip_state = self.get_initial_flip_state()
        self.update_card_display()

    def apply_filters(self):
        selected_cat = self.cat_var.get()
        query = self.search_var.get().strip().lower()

        filtered = []
        for cat, card in self.all_cards:
            if selected_cat != "All Categories" and cat != selected_cat:
                continue

            abbr = str(card.get("abbreviation", "")).lower()
            proto = str(card.get("protocol", "")).lower()
            desc = str(card.get("description", "")).lower()

            if query and (query not in abbr and query not in proto and query not in desc):
                continue

            filtered.append((cat, card))

        self.active_cards = filtered
        self.current_index = 0
        self.flip_state = self.get_initial_flip_state()
        self.update_card_display()

    def shuffle_current(self):
        if self.active_cards:
            random.shuffle(self.active_cards)
            self.current_index = 0
            self.flip_state = self.get_initial_flip_state()
            self.update_card_display()

    def reset_filter(self):
        self.cat_var.set("All Categories")
        self.search_var.set("")
        self.start_view_var.set("Term / Port")
        self.apply_filters()
        self.shuffle_current()

    def update_card_display(self):
        if not self.active_cards:
            self.category_label.config(text="No cards match the current search.")
            self.card_title.config(text="")
            self.card_text.config(text="No matching cards found.", fg="#F5F9FF", font=("Segoe UI", 20, "bold"))
            self.flip_hint.config(text="Try adjusting the category or search term")
            self.counter_label.config(text="0 / 0")
            return

        cat, card = self.active_cards[self.current_index]
        has_protocol = bool(card.get("protocol"))

        effective_state = self.flip_state
        if not has_protocol and effective_state == 1:
            effective_state = 2

        if effective_state == 0:
            stage = "Term / Port" if has_protocol else "Term"
            display_text = card.get("abbreviation", "N/A")
            card_title_text = "Front of card"
            title_color = "#8DD1FF"
            font_spec = ("Segoe UI", 28, "bold")
            text_color = "#7DC4FF"
            self.flip_hint.config(text="Press Space or click to reveal protocol")
        elif effective_state == 1:
            stage = "Protocol"
            display_text = card.get("protocol", "N/A")
            card_title_text = "Protocol"
            title_color = "#8AF0A2"
            font_spec = ("Segoe UI", 24, "bold")
            text_color = "#7CF0A0"
            self.flip_hint.config(text="Press Space or click to reveal description")
        else:
            stage = "Description"
            display_text = card.get("description", "N/A")
            card_title_text = "Description"
            title_color = "#F7F9FC"
            font_spec = ("Segoe UI", 16, "normal")
            text_color = "#F7F9FC"
            self.flip_hint.config(text="Press Space or click to move to the next card")

        self.category_label.config(text=f"Category: {cat}   •   {stage} view")
        self.card_title.config(text=card_title_text, fg=title_color)
        self.card_text.config(text=display_text, fg=text_color, font=font_spec)
        self.counter_label.config(text=f"Card {self.current_index + 1} of {len(self.active_cards)}")

    def flip_card(self):
        if self.active_cards:
            card = self.active_cards[self.current_index][1]
            has_protocol = bool(card.get("protocol"))

            if has_protocol:
                self.flip_state = (self.flip_state + 1) % 3
            else:
                self.flip_state = 2 if self.flip_state == 0 else 0

            self.update_card_display()

    def next_card(self):
        if self.active_cards:
            self.current_index = (self.current_index + 1) % len(self.active_cards)
            self.flip_state = self.get_initial_flip_state()
            self.update_card_display()

    def prev_card(self):
        if self.active_cards:
            self.current_index = (self.current_index - 1) % len(self.active_cards)
            self.flip_state = self.get_initial_flip_state()
            self.update_card_display()


if __name__ == "__main__":
    app = FlashcardApp()
    app.mainloop()