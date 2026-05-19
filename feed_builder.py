#prototype.txt

def get_user_interests():
    interests = input("What are three of your interests? (separate with commas)\n> ")
    return [i.strip().lower() for i in interests.split(",")]


# Category dictionaries
sports = [
    "tennis", "basketball", "soccer", "football", "baseball",
    "volleyball", "golf", "swimming", "skiing", "snowboarding",
    "boxing", "wrestling", "cricket", "rugby", "track", "cycling"
]

culinary = [
    "food", "cooking", "baking", "pasta", "coffee", "dessert",
    "cake", "bread", "smoothie", "recipe", "meal", "dinner",
    "lunch", "breakfast", "vegan", "vegetarian", "snacks"
]

physical = [
    "fitness", "workout", "gym", "lifting", "running",
    "cardio", "pilates", "yoga", "exercise", "training",
    "stretching", "abs", "strength"
]

material = [
    "fashion", "clothes", "outfits", "style", "shoes",
    "streetwear", "accessories", "jewelry", "bags"
]


def categorize_interest(word):
    if word in sports:
        return "sports"
    elif word in culinary:
        return "culinary"
    elif word in physical:
        return "physical"
    elif word in material:
        return "material"
    else:
        return "other"


def generate_pins(interests):
    pins = []

    for word in interests:
        category = categorize_interest(word)

        if category == "sports":
            pins.append(f"{word} drills for beginners")
            pins.append(f"{word} workout routine")
            pins.append(f"{word} outfit inspiration")

        elif category == "culinary":
            pins.append(f"{word} recipes to try")
            pins.append(f"easy {word} ideas")
            pins.append(f"best {word} dishes")

        elif category == "physical":
            pins.append(f"{word} workout routine")
            pins.append(f"{word} exercises for beginners")
            pins.append(f"{word} training plan")

        elif category == "material":
            pins.append(f"{word} outfit ideas")
            pins.append(f"{word} style inspiration")
            pins.append(f"trending {word} looks")

        else:
            pins.append(f"{word} ideas")
            pins.append(f"{word} inspiration")

    return pins


def main():
    interests = get_user_interests()

    print("\nYour Interests Categorized:\n")
    for word in interests:
        print(f"{word} → {categorize_interest(word)}")

    pins = generate_pins(interests)

    print("\nGenerated Pins:\n")
    for pin in pins:
        print("-", pin)


main()
