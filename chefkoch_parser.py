import os
from urllib.request import urlopen

from bs4 import BeautifulSoup, Tag
from lxml import etree


def get_ingredients(parsed):
    ingredients_table = parsed.find(class_="ingredients")
    ingredients_amount = []
    ingredients_name = []
    for ingredient_row in ingredients_table:
        if not isinstance(ingredient_row, Tag):
            continue

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
    dom = etree.HTML(str(parsed))
    instruction_html = dom.xpath('/html/body/main/article[4]/div[1]')[0]
    instruction_string = ""
    for instructionHtml in instruction_html.itertext():
        instruction_string += str(instructionHtml)
    instructions_split = instruction_string.split(chr(10))
    instructions = [x.lstrip() for x in instructions_split if not is_whitespace(x)]
    return instructions


def is_whitespace(string):
    return len(string) == 0 or string.isspace()


def generate_md(i, recipe_title, ingredients_amount, ingredients_name, instructions):
    recipe_title = "".join(x for x in recipe_title if x.isalnum())
    with open(os.path.join('recipes', f'{recipe_title.replace(" ","_")}.md'), 'w') as f:
        content = f'# {recipe_title}\n\n'
        pic = "picture" + str(i) + ".jpg"
        content = f'![{recipe_title} - Picture]({pic} "Example Picture - ")\n\n'

        content += '## Ingredients\n'
        content += '| Menge | Zutat |\n'
        content += '| ----- | ----- |\n'
        for j, amount in enumerate(ingredients_amount):
            while amount != amount.replace('  ', ' '):
                amount = amount.replace('  ', ' ')
            content += f'| {amount} | {ingredients_name[j]} |\n'

        content += '\n## Instructions\n'
        for instr in instructions:
            content += f'- {instr}\n'
        f.write(content)


def little_do_it_all():
    with open("urls.txt") as f:
        urls = f.readlines()
    urls = [url.strip() for url in urls]

    for i, url in enumerate(urls):
        page = urlopen(url)
        parsed = BeautifulSoup(page, 'html.parser')
        ingredients_amount, ingredients_name = get_ingredients(parsed)
        instructions = get_instructions(parsed)
        recipe_title = parsed.find("title").string
        # TODO: FIX PICTURES
        dom = etree.HTML(str(parsed))
        picture_url = dom.xpath('//*[@id="i-amp-0"]/img/@src')[0]
        picture_response = urlopen(picture_url)
        picture = picture_response.read()

        try:
            with open("recipes/picture" + str(i) + ".jpg", "wb+") as f:
                f.write(picture)
        except OSError:
            print("Error trying to write picture to filesystem.")

        generate_md(i, recipe_title, ingredients_amount, ingredients_name, instructions)


if __name__ == "__main__":
    little_do_it_all()
