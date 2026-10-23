"""Generate sample demonstration images for Module 18 Multimodal Concierge."""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

DATA_DIR = Path("data")
SAMPLE_DIR = DATA_DIR / "sample_images"
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)


def create_menu_image(path: Path):
    img = Image.new("RGB", (800, 600), color=(250, 248, 240))
    d = ImageDraw.Draw(img)
    # Header border
    d.rectangle([(20, 20), (780, 580)], outline=(180, 140, 60), width=4)
    d.rectangle([(28, 28), (772, 572)], outline=(220, 200, 150), width=2)
    # Title
    d.text((220, 50), "AZURE BREEZE SEAFOOD GRILL", fill=(40, 60, 90))
    d.text((310, 80), "~ Dinner Carte du Jour ~", fill=(160, 120, 40))
    d.line([(150, 115), (650, 115)], fill=(180, 140, 60), width=2)

    # Entrees
    d.text((60, 140), "PAN-SEARED CHILEAN SEA BASS ..................................... $58", fill=(30, 30, 30))
    d.text((80, 165), "Truffle sunchoke puree, blistered baby heirloom tomatoes, lemon-thyme emulsion (GF/DF)", fill=(90, 90, 90))

    d.text((60, 210), "MEDITERRANEAN COASTAL BOUILLABAISSE ........................ $48", fill=(30, 30, 30))
    d.text((80, 235), "Fresh local red snapper, tiger prawns, blue mussels, saffron broth, rouille crostini", fill=(90, 90, 90))

    d.text((60, 280), "WOOD-GRILLED OCTOPUS WITH SMOKED PAPRIKA ......... $36", fill=(30, 30, 30))
    d.text((80, 305), "Crispy fingerling potatoes, caper chimichurri, taggiasca olives (GF)", fill=(90, 90, 90))

    d.text((60, 350), "HANDMADE SQUID INK TAGLIOLINI ALL'ASTICE ................ $52", fill=(30, 30, 30))
    d.text((80, 375), "Half Maine lobster, cherry pomodorini, Calabrian chili, garlic parsley oil", fill=(90, 90, 90))

    d.line([(250, 430), (550, 430)], fill=(200, 180, 130), width=1)
    d.text((120, 450), "All dietary requests (Gluten-Free, Halal, Nut Allergies) accommodated with care.", fill=(120, 100, 50))
    d.text((250, 480), "Chef de Cuisine: Marco De Luca | Les Clefs d'Or Selection", fill=(60, 80, 110))

    img.save(path, quality=92)


def create_map_image(path: Path):
    img = Image.new("RGB", (800, 600), color=(240, 245, 250))
    d = ImageDraw.Draw(img)
    # Border
    d.rectangle([(15, 15), (785, 585)], outline=(30, 80, 140), width=4)
    d.text((240, 35), "THE GRAND AZURE RESORT & SPA - PROPERTY MAP", fill=(20, 50, 100))
    d.line([(100, 65), (700, 65)], fill=(30, 80, 140), width=2)

    # Buildings & Zones
    # Main Tower
    d.rectangle([(80, 100), (320, 300)], fill=(210, 225, 245), outline=(50, 90, 150), width=3)
    d.text((120, 120), "MAIN RESORT PALACE", fill=(20, 40, 80))
    d.text((100, 150), "• Reception & Porte-Cochere", fill=(40, 40, 40))
    d.text((100, 180), "• Level 1: Concierge Desk", fill=(40, 40, 40))
    d.text((100, 210), "• Le Jardin French Bistro", fill=(40, 40, 40))
    d.text((100, 240), "• Grand Ballroom & Gallery", fill=(40, 40, 40))

    # Infinity Pool Deck
    d.rectangle([(380, 100), (720, 300)], fill=(180, 225, 250), outline=(20, 130, 200), width=3)
    d.text((450, 120), "INFINITY POOL & SUNSET CABANAS", fill=(10, 70, 130))
    d.text((410, 160), "• Heated 82°F Horizon Pool (Adults quiet hours 8 PM)", fill=(20, 60, 100))
    d.text((410, 190), "• Poolside Bar & Raw Seafood Counter", fill=(20, 60, 100))
    d.text((410, 220), "• Private VIP Lounging Cabanas 1 - 8", fill=(20, 60, 100))

    # Spa Pavilion
    d.rectangle([(80, 350), (320, 530)], fill=(235, 245, 235), outline=(60, 140, 80), width=3)
    d.text((110, 370), "THE AZURE WELLNESS SPA", fill=(30, 90, 40))
    d.text((100, 400), "• Hydrotherapy Vitality Pools", fill=(40, 70, 50))
    d.text((100, 430), "• Himalayan Salt Saunas & Steam", fill=(40, 70, 50))
    d.text((100, 460), "• 8 Private Treatment Suites", fill=(40, 70, 50))
    d.text((100, 490), "• 24/7 Fitness Pavilion (Cardio/Weights)", fill=(40, 70, 50))

    # Cliffside Promenade & Marina Gate
    d.rectangle([(380, 350), (720, 530)], fill=(250, 235, 220), outline=(190, 100, 40), width=3)
    d.text((430, 370), "CLIFFSIDE PROMENADE & MARINA", fill=(140, 60, 20))
    d.text((410, 400), "• Azure Breeze Cliffside Grill & Terrace", fill=(100, 50, 20))
    d.text((410, 430), "• Sunset Cliffside Lounge & Firepits", fill=(100, 50, 20))
    d.text((410, 460), "• Marina Boardwalk & Yacht Charter Pier", fill=(100, 50, 20))
    d.text((410, 490), "• Electric Coastal Shuttle Departure", fill=(100, 50, 20))

    img.save(path, quality=92)


def create_dish_image(path: Path):
    img = Image.new("RGB", (800, 600), color=(25, 25, 30))
    d = ImageDraw.Draw(img)
    # Slate Plate
    d.ellipse([(150, 50), (650, 550)], fill=(45, 48, 55), outline=(75, 80, 90), width=6)
    # Sauce Swirl
    d.ellipse([(220, 180), (580, 460)], outline=(210, 185, 120), width=8)
    # Sunchoke Truffle Puree Bed
    d.ellipse([(280, 230), (520, 400)], fill=(235, 225, 195))
    # Sea Bass Fillet
    d.rectangle([(320, 260), (480, 370)], fill=(245, 240, 235), outline=(140, 90, 40), width=5)
    # Crispy Golden Skin Lines
    for y in range(275, 360, 18):
        d.line([(325, y), (475, y)], fill=(160, 95, 30), width=3)
    # Microgreen & Cherry Tomato Garnish
    d.ellipse([(340, 280), (360, 300)], fill=(200, 40, 30))
    d.ellipse([(430, 320), (450, 340)], fill=(220, 50, 40))
    d.ellipse([(380, 250), (410, 270)], fill=(40, 160, 50))
    d.ellipse([(440, 270), (460, 290)], fill=(50, 180, 60))

    # Caption Banner
    d.rectangle([(50, 520), (750, 580)], fill=(20, 20, 25), outline=(180, 140, 60), width=2)
    d.text((100, 535), "FEATURED DISH: Pan-Seared Chilean Sea Bass with Truffle Puree", fill=(240, 220, 160))
    d.text((100, 555), "Venue: Azure Breeze Seafood Grill | Pairing: Domaine Leflaive Puligny-Montrachet", fill=(170, 170, 170))

    img.save(path, quality=92)


def create_attraction_image(path: Path):
    img = Image.new("RGB", (800, 600), color=(135, 206, 235))
    d = ImageDraw.Draw(img)
    # Sea / Water
    d.rectangle([(0, 350), (800, 600)], fill=(0, 105, 148))
    # Turquoise Bioluminescent Grotto Water
    d.ellipse([(150, 380), (650, 580)], fill=(64, 224, 208))
    # Limestone Cliffs / Cave Arch
    d.polygon([(0, 600), (0, 150), (180, 100), (320, 220), (280, 380), (120, 550)], fill=(140, 120, 100))
    d.polygon([(800, 600), (800, 120), (620, 90), (480, 220), (520, 390), (680, 560)], fill=(140, 120, 100))
    # Sea Cave Archway Span
    d.ellipse([(250, 120), (550, 350)], fill=(135, 206, 235), outline=(110, 90, 70), width=10)
    # Kayak
    d.ellipse([(360, 440), (440, 460)], fill=(255, 140, 0))

    # Caption Banner
    d.rectangle([(50, 520), (750, 580)], fill=(20, 35, 55), outline=(64, 224, 208), width=2)
    d.text((120, 535), "EMERALD COVE SEA CAVES & BIOLUMINESCENT GROTTOES", fill=(255, 255, 255))
    d.text((120, 555), "Distance: 2.4 km from Resort | Access: Resort Eco-Boat or Morning Sea Kayak", fill=(200, 240, 240))

    img.save(path, quality=92)


def create_thermostat_image(path: Path):
    img = Image.new("RGB", (800, 600), color=(220, 220, 220))
    d = ImageDraw.Draw(img)
    # Wall Mounting Plate
    d.rectangle([(150, 80), (650, 520)], fill=(245, 245, 245), outline=(170, 170, 170), width=5)
    # Digital LCD Screen
    d.rectangle([(200, 130), (600, 380)], fill=(10, 25, 40), outline=(60, 80, 100), width=4)
    # LCD Readout
    d.text((250, 160), "68 °F", fill=(100, 200, 255))
    d.text((450, 170), "SET: 68°F", fill=(180, 220, 255))
    d.text((250, 240), "[*] MODE: COOL (SNOWFLAKE ACTIVE)", fill=(120, 240, 160))
    d.text((250, 280), "TERRACE DOOR SENSOR: [CLOSED & LATCHED]", fill=(120, 240, 160))
    d.text((250, 320), "FAN STATUS: HIGH AUTO CIRCULATION", fill=(100, 200, 255))

    # Physical Buttons
    d.rectangle([(230, 420), (320, 480)], fill=(200, 200, 200), outline=(120, 120, 120), width=2)
    d.text((255, 445), "TEMP -", fill=(40, 40, 40))

    d.rectangle([(355, 420), (445, 480)], fill=(70, 130, 220), outline=(40, 80, 160), width=2)
    d.text((375, 445), "POWER", fill=(255, 255, 255))

    d.rectangle([(480, 420), (570, 480)], fill=(200, 200, 200), outline=(120, 120, 120), width=2)
    d.text((505, 445), "TEMP +", fill=(40, 40, 40))

    img.save(path, quality=92)


def generate_all_samples():
    create_menu_image(SAMPLE_DIR / "azure_breeze_menu.jpg")
    create_map_image(SAMPLE_DIR / "hotel_resort_map.jpg")
    create_dish_image(SAMPLE_DIR / "signature_sea_bass.jpg")
    create_attraction_image(SAMPLE_DIR / "emerald_cove_sea_caves.jpg")
    create_thermostat_image(SAMPLE_DIR / "in_room_thermostat.jpg")


if __name__ == "__main__":
    generate_all_samples()
    print("All sample images generated successfully!")
