import scrapy
import json

class PokemonScrapper(scrapy.Spider):
    name = 'pokemon_scrapper'
    domain = "https://pokemondb.net/"
    start_urls = ["https://pokemondb.net/pokedex/all"]

    # Inicializa a lista para armazenar os dados dos Pokémons
    pokemons_data = []

    def parse(self, response):
        pokemons = response.css('#pokedex > tbody > tr')
        for pokemon in pokemons:
            link = pokemon.css("td.cell-name > a::attr(href)").extract_first()
            yield response.follow(self.domain + link, self.parse_pokemon)

    def parse_pokemon(self, response):
        pokemon_id = response.css(
            '.vitals-table > tbody > tr:nth-child(1) > td > strong::text'
        ).get()
        pokemon_name = response.css('#main > h1::text').get()

        # Captura as próximas evoluções (se houver)
        evolutions = response.css(
            '#main > div.infocard-list-evo > div > span.infocard-lg-data.text-muted'
        )
        next_evolutions = []
        for evolution in evolutions:
            evo_num = evolution.css('small::text').get()
            evo_name = evolution.css('a::text').get()
            evo_link = self.domain + evolution.css('a::attr(href)').get()
            next_evolutions.append({
                'evo_num': evo_num,
                'evo_name': evo_name,
                'evo_link': evo_link
            })

        # Captura o peso do Pokémon
        weight_text = response.css(
            '.vitals-table > tbody > tr:contains("Weight") > td::text'
        ).get()
        weight = weight_text.split(' ')[0] if weight_text else None

        # Captura o tamanho do Pokémon
        height_text = response.css(
            '.vitals-table > tbody > tr:contains("Height") > td::text'
        ).get()
        height = height_text.split(' ')[0] if height_text else None

        # Captura os tipos do Pokémon
        types = response.css(
            '.vitals-table > tbody > tr:contains("Type") > td a::text'
        ).getall()

        # Captura habilidades com URLs
        abilities = []
        ability_links = response.css(
            '.vitals-table > tbody > tr:contains("Abilities") > td a'
        )
        for link in ability_links:
            ability_name = link.css('::text').get()
            ability_url = self.domain + link.css('::attr(href)').get()
            abilities.append({'ability_name': ability_name, 'ability_url': ability_url})

        # Adiciona os dados do Pokémon à lista
        self.pokemons_data.append({
            'pokemon_id': int(pokemon_id),  # Converte para int para garantir a ordenação correta
            'pokemon_name': pokemon_name,
            'next_evolutions': next_evolutions,
            'pokemon_weight': weight,
            'pokemon_height': height,
            'pokemon_types': types,
            'pokemon_abilities': abilities
        })

    def closed(self, reason):
        # Ordena os Pokémons pelo 'pokemon_id'
        self.pokemons_data.sort(key=lambda x: x['pokemon_id'])

        # Salva os dados ordenados no arquivo JSON
        with open('pokemons.json', 'w', encoding='utf-8') as f:
            json.dump(self.pokemons_data, f, ensure_ascii=False, indent=4)
