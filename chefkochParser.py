from bs4 import BeautifulSoup, Tag
from pylatex import Document, Section, LongTabu, LargeText, VerticalSpace, Figure, Center
from pylatex.utils import bold
from urllib.request import urlopen


def get_ingredients(parsed):
    ingredients_table = parsed.find(class_="incredients")
    ingredients_amount = []
    ingredients_name = []
    for ingredient_row in ingredients_table:
        if isinstance(ingredient_row, Tag):
            columns = ingredient_row.find_all('td')
            for j, column in enumerate(columns):
                parsed_string = ""
                if column.a:
                    parsed_string = column.a.string.strip().replace("\xa0", " ")
                else:
                    if column.sup:
                        strings = column.get_text()
                        for s in strings:
                            if s.isalpha():
                                parsed_string += " "
                                parsed_string += s
                            else:
                                parsed_string += s
                    else:
                        parsed_string = column.get_text().strip().replace("\xa0", " ")
                if j % 2 == 1:
                    ingredients_name.append(parsed_string)
                else:
                    ingredients_amount.append(parsed_string)
    return ingredients_amount, ingredients_name


def get_instructions(parsed):
    instructions_html = parsed.find(id="rezept-zubereitung").strings
    instructions = ""
    for instructionHtml in instructions_html:
        instructions += instructionHtml
    return instructions


def generate_tex(i, recipe_title, ingredients_amount, ingredients_name, instructions):
    geometry_options = {
        "head": "30pt",
        "margin": "0.6in",
        "bottom": "0.8in",
    }
    doc = Document(geometry_options=geometry_options)
    doc.add_color("strongRed", "HTML", "f44242")
    doc.add_color("lightRed", "HTML", "ffc1c1")
    with doc.create(Center()):
        doc.append(LargeText(bold(recipe_title)))
    doc.append(VerticalSpace("0pt"))
    with doc.create(Section("Zutaten", False)):
        with doc.create(LongTabu("X[l] X[3l]", row_height=1.5)) as ingredientTable:
            ingredientTable.add_row(["Menge", "Zutat"], mapper=bold, color="strongRed")
            ingredientTable.add_hline()
            for j, ingredientAmount in enumerate(ingredients_amount):
                row = [ingredientAmount, ingredients_name[j]]
                if (j % 2) == 0:
                    ingredientTable.add_row(row, color="lightRed")
                else:
                    ingredientTable.add_row(row)
    doc.append(VerticalSpace("0pt"))
    with doc.create(Section("Anweisungen", False)):
        doc.append(instructions)
    with doc.create(Figure(position="b!")) as pic:
        pic.add_image("picture" + str(i) + ".jpg", width="220px")
    path = "recipes/" + recipe_title.replace(" ", "")
    print("Created:" + path + ".tex")
    try:
        doc.generate_tex(path)
    except Exception:
        pass


def little_do_it_all():
    with open("urls.txt") as f:
        urls = f.readlines()
    urls = [url.strip() for url in urls]

    for i, url in enumerate(urls):
        page = urlopen(url)
        parsed = BeautifulSoup(page, 'html.parser')
        ingredients_amount, ingredients_name = get_ingredients(parsed)
        instructions = get_instructions(parsed)
        recipe_title = parsed.find(class_="page-title").string
        picture_url = parsed.find(class_="slideshow-image").attrs['src']
        picture_response = urlopen(picture_url)
        picture = picture_response.read()
        try:
            with open("recipes/picture" + str(i) + ".jpg", "wb+") as f:
                f.write(picture)
        except OSError:
            print("Error trying to write picture to filesystem.")
        generate_tex(i, recipe_title, ingredients_amount, ingredients_name, instructions)


little_do_it_all()
