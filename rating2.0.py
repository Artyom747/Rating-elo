import json
import os
import sys
import tempfile
import shutil

class RacingApp:
    def __init__(self):
        self.data_file = "pilots_data.json"
        self.pilots = []
        self.load_data()

    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r") as file:
                    data = json.load(file)
                    if isinstance(data, list):
                        self.pilots = data
                    else:
                        print("Invalid data format in file. Expected a list.")
                        self.pilots = []
        except Exception as e:
            print(f"Error loading data: {e}")

    def save_data(self):
        try:
            temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
            with open(temp_file.name, "w") as file:
                json.dump(self.pilots, file, indent=4)
            shutil.move(temp_file.name, self.data_file)
        except Exception as e:
            print(f"Error saving data: {e}")

    def add_pilot(self, name):
        if not name:
            print("Pilot name cannot be empty.")
            return
        if any(pilot["name"] == name for pilot in self.pilots):
            print(f"Pilot '{name}' already exists.")
            return
        self.pilots.append({"name": name, "rating": 1200, "delta": None})
        self.save_data()
        print(f"Pilot '{name}' added successfully.")

    def delete_pilot(self, name):
        initial_count = len(self.pilots)
        self.pilots = [pilot for pilot in self.pilots if pilot["name"] != name]
        if len(self.pilots) < initial_count:
            self.save_data()
            print(f"Pilot '{name}' deleted successfully.")
        else:
            print(f"Pilot '{name}' not found.")

    def calculate_elo_ratings(self):
        # Выбор пилотов для гонки
        print("\nSelect pilots participating in the race:")
        for idx, pilot in enumerate(self.pilots):
            print(f"{idx}. {pilot['name']}")

        selected_input = input("Enter pilot numbers separated by space: ").strip()
        selected_indices = []
        for s in selected_input.split():
            if s.isdigit():
                idx = int(s)
                if 0 <= idx < len(self.pilots):
                    selected_indices.append(idx)
                else:
                    print(f"Invalid index: {s}. Skipping.")
            else:
                print(f"Invalid input: {s}. Skipping.")

        if len(selected_indices) < 2:
            print("At least two pilots must be selected to calculate ratings.")
            return

        selected_names = [self.pilots[i]['name'] for i in selected_indices]
        print(f"Selected pilots: {', '.join(selected_names)}")

        # Сбор позиций
        positions = {}
        valid_pilots = []
        for name in selected_names:
            while True:
                position = input(f"Enter position for {name} (must be a positive integer): ").strip()
                if position.isdigit():
                    pos = int(position)
                    if pos > 0:
                        if pos in positions.values():
                            print(f"Position {pos} is already taken. Please enter a unique position.")
                            continue
                        positions[name] = pos
                        valid_pilots.append(name)
                        break
                    else:
                        print(f"Invalid position for {name}: Position must be greater than 0.")
                else:
                    print(f"Invalid position for {name}: Not a number.")

        if len(valid_pilots) < 2:
            print("Not enough valid positions specified to calculate ratings.")
            return

        # Расчет рейтингов
        pilots = [pilot for pilot in self.pilots if pilot["name"] in valid_pilots]
        pilots = sorted(pilots, key=lambda p: positions[p["name"]])

        old_ratings = {pilot["name"]: pilot["rating"] for pilot in pilots}
        K = 32

        for i, pilot_a in enumerate(pilots):
            total_change = 0
            for j, pilot_b in enumerate(pilots):
                if i == j:
                    continue
                ra = pilot_a["rating"]
                rb = pilot_b["rating"]
                expected_score = 1 / (1 + 10 ** ((rb - ra) / 400))
                actual_score = 1 if positions[pilot_a["name"]] < positions[pilot_b["name"]] else 0
                rating_change = K * (actual_score - expected_score)
                total_change += rating_change
            pilot_a["rating"] = round(pilot_a["rating"] + total_change)
            pilot_a["delta"] = pilot_a["rating"] - old_ratings[pilot_a["name"]]

        # Обновление данных
        for pilot in self.pilots:
            if pilot["name"] in old_ratings:
                updated_pilot = next(p for p in pilots if p["name"] == pilot["name"])
                pilot["rating"] = updated_pilot["rating"]
                pilot["delta"] = updated_pilot["delta"]

        self.save_data()
        print("ELO ratings calculated successfully.")

    def display_pilots(self):
        if not self.pilots:
            print("No pilots available.")
            return

        def supports_color():
            """
            Returns True if the running system's terminal supports color, and False otherwise.
            """
            plat = sys.platform
            supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)
            is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
            return supported_platform and is_a_tty

        if supports_color():
            GREEN = "\033[92m"
            RED = "\033[91m"
            RESET = "\033[0m"
        else:
            GREEN = ""
            RED = ""
            RESET = ""

        print("\nCurrent Pilots:")
        print(f"{'Name':<20}{'Rating':<10}{'Delta':<10}")
        for pilot in sorted(self.pilots, key=lambda p: p["rating"], reverse=True):
            delta = pilot.get("delta")
            delta_str = f"{delta:+d}" if delta is not None else "N/A"

            if delta is not None:
                if delta > 0:
                    delta_str = f"{GREEN}{delta_str}{RESET}"
                elif delta < 0:
                    delta_str = f"{RED}{delta_str}{RESET}"

            print(f"{pilot['name']:<20}{pilot['rating']:<10}{delta_str:<10}")


def main():
    app = RacingApp()
    while True:
        print("\nRacing Rating (ELO System)")
        print("1. Add Pilot")
        print("2. Delete Pilot")
        print("3. Calculate ELO Ratings")
        print("4. Display Pilots")
        print("5. Exit")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            name = input("Enter pilot name: ").strip()
            app.add_pilot(name)
        elif choice == "2":
            name = input("Enter pilot name to delete: ").strip()
            app.delete_pilot(name)
        elif choice == "3":
            app.calculate_elo_ratings()
        elif choice == "4":
            app.display_pilots()
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()