from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString, Tag
from pylatex import Document, Section, Subsection, Command, LongTabu
from pylatex.utils import bold
import string

with open("urls.txt") as f:
    urls = f.readlines()
urls = [url.strip() for url in urls]

for url in urls:
    page = urlopen(url)
    parsed = BeautifulSoup(page, 'html.parser')
    ingredientsTable = parsed.find(True, class_="incredients")
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
                        column.sup.unwrap()
                        column.sub.unwrap()
                        strings = column.stripped_strings
                        for s in strings:
                            if s.isalpha():
                                parsedString += " "
                                parsedString += s
                            else:
                                parsedString += s
                        #parsedString = column.strip().replace("\xa0", " ")
                    else:
                        parsedString = column.string.strip().replace("\xa0", " ")
                if i%2 == 1:
                    ingredientsName.append(parsedString)
                else:
                    ingredientsAmount.append(parsedString)
                i += 1

    print(ingredientsAmount)
    print(ingredientsName)

    instructionsHtml = parsed.find(id="rezept-zubereitung").strings
    instructions = ""
    for instructionHtml in instructionsHtml:
        instructions += instructionHtml
    print(instructions.strip())

doc = Document('Recipe')
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

doc.generate_pdf("recipe", clean_tex=False)
