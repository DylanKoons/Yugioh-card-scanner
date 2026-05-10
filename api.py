import requests

class YGOProDeckAPI:
    BASE_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"

    @staticmethod
    def search_by_set_code(set_code):
        """Search for cards by set code"""
        try:
            print(f"Searching for set code: {set_code}")
            response = requests.get(YGOProDeckAPI.BASE_URL, timeout=15)
            response.raise_for_status()
            data = response.json()

            if "data" not in data or not isinstance(data["data"], list):
                print("Invalid API response structure")
                return None

            # Search for cards matching the set code
            matches = []
            set_code_upper = set_code.upper()

            for card in data["data"]:
                if "card_sets" in card:
                    for card_set in card["card_sets"]:
                        card_set_code = card_set.get("set_code", "").upper()
                        if set_code_upper == card_set_code:
                            matches.append({
                                "name": card.get("name"),
                                "type": card.get("type"),
                                "atk": card.get("atk"),
                                "def": card.get("def"),
                                "level": card.get("level"),
                                "desc": card.get("desc"),
                                "set_code": card_set.get("set_code"),
                                "set_rarity": card_set.get("set_rarity"),
                                "set_price": card_set.get("set_price")
                            })

            if matches:
                print(f"Found {len(matches)} card(s) for set code {set_code}")
            else:
                print(f"No cards found for set code {set_code}")

            return matches if matches else None
        except requests.RequestException as e:
            print(f"API Error: {e}")
            return None
        except Exception as e:
            print(f"Error processing API response: {e}")
            return None

