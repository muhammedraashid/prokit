
def global_data(request):
    size_options = {
        "Boots": ["38", "39", "40", "41", "42", "43", "44", "45"],
        "Shorts": ["XS", "S", "M", "L", "XL"],
        "Balls": ["Size 3", "Size 4", "Size 5"],
        "Jersey": ["XS", "S", "M", "L", "XL"],
        "Socks": ["S", "M", "L"],
    }
    
    colors = [
        "Red", "Blue", "Green", "Black", "White", "Yellow", "Orange", "Purple",
        "Pink", "Brown", "Gray", "Navy", "Gold"
    ]
    brands = ["Nike", "Puma", "Adidas", "Jordan", "New Balance", "Nivia", "Kenza", "Sega"]

    return {
        "size_options": size_options,
        "colors": colors,
        "brands": brands
    }