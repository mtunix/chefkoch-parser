from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString, Tag
from pylatex import Document, Section, Subsection, Command, LongTabu, MiniPage, LargeText, LineBreak, VerticalSpace, Figure
from pylatex.utils import bold
import string

with open("urls.txt") as f:
    urls = f.readlines()
urls = [url.strip() for url in urls]

geometry_options = {
    "head": "30pt",
    "margin": "0.6in",
    "bottom": "0.8in",
}

for url in urls:
    page = urlopen(url)
    parsed = BeautifulSoup(page, 'html.parser')
    ingredientsTable = parsed.find(class_="incredients")
    ingredientsAmount = []
    ingredientsName = []
    for row in ingredientsTable:
        if isinstance(row, Tag):
            columns = row.find_all('td');
            i = 0
            for column in columns:
                parsedString = ""
                if column.a:
                    parsedString = column.a.string.strip().replace("\xa0", " ")
                else:
                    if column.sup:
                        #column.sup.unwrap()
                        #column.sub.unwrap()
                        #strings = column.stripped_strings
                        strings = column.get_text()
                        for s in strings:
                            if s.isalpha():
                                parsedString += " "
                                parsedString += s
                            else:
                                parsedString += s
                    else:
                        parsedString = column.get_text().strip().replace("\xa0", " ")
                if i%2 == 1:
                    ingredientsName.append(parsedString)
                else:
                    ingredientsAmount.append(parsedString)
                i += 1
    instructionsHtml = parsed.find(id="rezept-zubereitung").strings
    instructions = ""
    for instructionHtml in instructionsHtml:
        instructions += instructionHtml

    recipeTitle = parsed.find(class_="page-title").string
    pictureUrl = parsed.find(class_="slideshow-image").attrs['src']
    pictureResponse = urlopen(pictureUrl)
    picture = pictureResponse.read()
    try:
        with open("recipes/picture.jpg", "wb+") as f:
            f.write(picture)
    except OSError:
        pass
    doc = Document(geometry_options=geometry_options)
    doc.append(LargeText(bold(recipeTitle)))
    with doc.create(Figure(position="h!")) as pic:
        pic.add_image("picture.jpg")

    doc.append(VerticalSpace("25pt"))
    with doc.create(Section("Zutaten")):
        with doc.create(LongTabu("X[l] X[l]", row_height=1.5)) as ingredientTable:
            ingredientTable.add_row(["Menge", "Zutat"], mapper=bold, color="lightgray")
            ingredientTable.add_empty_row()
            ingredientTable.add_hline()
            for i in range(len(ingredientsAmount)):
                row = [ingredientsAmount[i], ingredientsName[i]]
                ingredientTable.add_row(row)
    with doc.create(Section("Anweisungen")):
            doc.append(instructions)

    path = "recipes/" + recipeTitle
    try:
        doc.generate_pdf(path, compiler_args=["-f", "-interaction=nonstopmode"])
    except Exception:
        pass
