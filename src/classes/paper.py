from datetime import datetime

from bs4 import BeautifulSoup
from html2text import HTML2Text


class Paper:
    def __init__(self, newspaper: str, url: str):
        self.newspaper = newspaper
        self.url = url
        self.author: str | None = None
        self.date: datetime | None = None
        self.tag: str | None = None
        self.title: str | None = None
        self.drophead: str | None = None
        self.excerpt: str | None = None
        self.body: str | None = None
        self.bodyHTML: str | None = None

        # configurar el parser de html
        self.parser = HTML2Text()
        self.parser.ignore_links = True
        self.parser.ignore_images = True
        self.parser.body_width = 0
        self.parser.skip_internal_links = True
        self.parser.unicode_snob = True

        # Desactivar formato Markdown
        self.parser.bold = False
        self.parser.italic = False
        self.parser.underline = False
        self.parser.mark_code = False
        self.parser.ignore_emphasis = True
        self.parser.skip_internal_links = True
        self.parser.single_line_break = True

    def __str__(self) -> str:
        return f"PAPER: {self.newspaper} \nURL: {self.url} \nAUTHOR: {self.author} \nDATE: {self.date} \nTAG: {self.tag} \nTITLE: {self.title} \nDROPHEAD: {self.drophead} \nEXPERT: {self.excerpt} \nBODY: {self.body}"

    def set_cooperativa_data(self, data: str) -> None:
        soup = BeautifulSoup(data, "html.parser")

        # AUTHOR
        author_elem = soup.select_one(".fecha-publicacion span")
        if author_elem is not None:
            self.author = author_elem.get_text(strip=True)

        # DATE
        date = self.url.split("/")[-2]
        self.date = datetime.strptime(date, "%Y-%m-%d")

        # TAG
        tag_container_elem = soup.select_one(".rotulo-topicos")
        if tag_container_elem:
            tags_elem = tag_container_elem.select("a span")
            if tags_elem:
                self.tag = tags_elem[0].get_text(strip=True)
        else:
            url_parts = self.url.split("/")
            if len(url_parts) > 4:
                self.tag = url_parts[4]

        # TITLE
        title_elem = soup.select_one("h1.titular")
        if title_elem:
            self.title = title_elem.get_text(strip=True)

        # DROPHEAD
        drophead_elem = soup.select_one(".contenedor-bajada .texto-bajada")
        if drophead_elem:
            drophead_html = drophead_elem.decode_contents(formatter="html")
            self.drophead = self.parser.handle(drophead_html).strip()

        # EXCERPT
        # BODY
        body_elem = soup.select_one(".contenedor-cuerpo .texto-bajada .cuerpo-articulo")
        if body_elem:
            for elem in body_elem.find_all("iframe"):
                elem.decompose()
            for elem in body_elem.find_all("script"):
                elem.decompose()
            for elem in body_elem.find_all("blockquote"):
                elem.decompose()
            for elem in body_elem.find_all("p", class_="prompt"):
                elem.decompose()

            body_html = body_elem.decode_contents(formatter="html")
            self.body = self.parser.handle(body_html).strip()
            self.bodyHTML = body_html

    def set_el_desconcierto_data(self, data: str) -> None:
        soup = BeautifulSoup(data, "html.parser")

        # AUTHOR
        author_elems = soup.select("article div.px-10.py-6.text-sm.font-normal.text-gray-600 span")
        if len(author_elems) > 0:
            self.author = author_elems[0].get_text(strip=True)
            # DATE
            self.date = datetime.strptime(author_elems[1].get_text(strip=True), "%d.%m.%Y")
        
        # TAG
        tag_elems = soup.select("div.flex.items-center.px-4.text-gray-400 span")
        if len(tag_elems) > 0:
            self.tag = tag_elems[-1].get_text(strip=True)

        # TITLE
        title_elem = soup.select_one("h1.text-xl.font-bold.text-white")
        if title_elem is not None:
            self.title = title_elem.get_text(strip=True)
        
        # DROPHEAD
        # EXCERPT
        excerpt_elem = soup.select_one("article div.px-10.py-6.text-lg.text-gray-700.bg-gray-100.border-l-4.border-brand-300")
        if excerpt_elem is not None:
            self.excerpt = excerpt_elem.get_text(strip=True)
        
        # BODY
        body_elem = soup.select_one("article div.single-post__content")
        if body_elem:
            for elem in body_elem.find_all("iframe"):
                elem.decompose()
            for elem in body_elem.find_all("script"):
                elem.decompose()
            for elem in body_elem.find_all("blockquote"):
                elem.decompose()
            for elem in body_elem.find_all("div"):
                elem.decompose()

            body_html = body_elem.decode_contents(formatter="html")
            self.body = self.parser.handle(body_html).strip()
            self.bodyHTML = body_html

    def set_el_mostrador_data(self, data: str) -> None:
        soup = BeautifulSoup(data, "html.parser")

        # AUTHOR
        if soup.select_one(".the-by__permalink"):
            author_elem = soup.select_one(".the-by__permalink")
            if author_elem is not None:
                self.author = author_elem.get_text(strip=True)
        elif soup.select_one(".the-single-author__permalink"):
            author_elem = soup.select_one(".the-single-author__permalink")
            if author_elem is not None:
                self.author = author_elem.get_text(strip=True)
                if soup.select_one(".the-single-author__subtitle"):
                    author_subtitle_elem = soup.select_one(".the-single-author__subtitle")
                    if author_subtitle_elem is not None:
                        author_subtitle = author_subtitle_elem.get_text(strip=True)
                        if author_subtitle != "":
                            self.author = f"{self.author}, {author_subtitle}"

        # DATE (yyyy-mm-dd)
        date_elem = soup.select_one(".d-the-single__date")
        if date_elem is not None:
            date_str = date_elem.get("datetime")
            if date_str is not None:
                self.date = datetime.strptime(date_str, "%Y-%m-%d")

        # TAG
        tag_elem = soup.select_one(".d-the-single-media__bag")
        if tag_elem is not None:
            self.tag = tag_elem.get_text(strip=True)

        # TITLE
        title_elem = soup.select_one(".d-the-single__title")
        if title_elem is not None:
            self.title = title_elem.get_text(strip=True)

        # DROPHEAD
        # EXCERPT
        excerpt_elem = soup.select_one(".d-the-single__excerpt")
        if excerpt_elem is not None:
            self.excerpt = excerpt_elem.get_text(strip=True)

        # BODY
        body_elem = soup.select_one(".d-the-single-wrapper__text")
        if body_elem is not None:
            for elem in body_elem.find_all("iframe"):
                elem.decompose()
            for elem in body_elem.find_all("script"):
                elem.decompose()
            for elem in body_elem.find_all("blockquote"):
                elem.decompose()
            for elem in body_elem.find_all("div", class_="responsive-container"):
                elem.decompose()
            for elem in body_elem.find_all("div", class_="the-single-cards"):
                elem.decompose()

            body_html = body_elem.decode_contents(formatter="html")
            self.body = self.parser.handle(body_html).strip()
            self.bodyHTML = body_html

    def set_emol_data(self, data: dict) -> None:
        # AUTHOR
        if data["autor"] is not None:
            self.author = data["autor"]

        # DATE
        if data["fechaPublicacion"] is not None:
            date = data["fechaPublicacion"].split("T")[0]
            self.date = datetime.strptime(date, "%Y-%m-%d")

        # TAG
        if data["subSeccion"] is not None:
            self.tag = data["subSeccion"]
        elif data["seccion"] is not None:
            self.tag = data["seccion"]

        # TITLE
        if data["titulo"] is not None:
            self.title = data["titulo"]

        # DROPHEAD
        if data["bajada"] is not None and len(data["bajada"]) > 0:
            self.drophead = data["bajada"][0]["texto"]

        # EXCERPT
        # BODY
        if data["texto"] is not None:
            self.body = self.parser.handle(data["texto"]).strip()
            self.bodyHTML = data["texto"]

    def set_radio_uchile_data(self, data: str) -> None:
        soup = BeautifulSoup(data, "html.parser")
        
        # AUTHOR
        # Post como columna de opinion
        author_elem = soup.select_one(".main-content ol.breadcrumb li.breadcrumb-item a")
        if author_elem is not None:
            self.author = author_elem.get_text(strip=True)
        else:
            # Cualquier otro post
            author_elem = soup.select(".post-header ul.meta li")
            if author_elem is not None:
                self.author = author_elem[0].get_text(strip=True)

        # DATE (dd-mm-yyyy)
        date_elem = soup.select(".post-header ul.meta li")
        if date_elem is not None:
            date_str = date_elem[-1].get_text(strip=True)
            self.date = datetime.strptime(date_str, "%d-%m-%Y")

        # TAG
        tag_elem = soup.select(".post-bottom a.tag")
        if tag_elem is not None and len(tag_elem) > 0:
            self.tag = tag_elem[-1].get_text(strip=True)

        # TITLE
        title_elem = soup.select_one(".post-header h1.title")
        if title_elem is not None:
            self.title = title_elem.get_text(strip=True)
        
        # DROPHEAD
        drophead_elem = soup.select_one(".post-header span.title")
        if drophead_elem is not None:
            self.drophead = drophead_elem.get_text(strip=True)
        
        # EXCERPT
        # BODY
        body_elem = soup.select_one(".main-content .post-content")
        if body_elem is not None:
            for elem in body_elem.find_all("iframe"):
                elem.decompose()
            for elem in body_elem.find_all("script"):
                elem.decompose()
            for elem in body_elem.find_all("blockquote"):
                elem.decompose()
        
            body_html = body_elem.decode_contents(formatter="html")
            self.body = self.parser.handle(body_html).strip()
            self.bodyHTML = body_html

    def set_tvn_data(self, data: str) -> None:
        soup = BeautifulSoup(data, "html.parser")

        # AUTHOR
        author_elem = soup.select_one(".cont-credits .author")
        if author_elem is not None:
            self.author = author_elem.get_text(strip=True)
            author_credit_elem = soup.select_one(".cont-credits .credit")
            if author_credit_elem is not None:
                self.author = f"{self.author}, {author_credit_elem.get_text(strip=True)}"

        # DATE
        date_elem = soup.select_one(".toolbar .fecha")
        if date_elem is not None:
            date_str = date_elem.get_text(strip=True)
            date_split = date_str.split(" ")

            months = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
            self.date = datetime(int(date_split[5]), months.index(date_split[3]) + 1, int(date_split[1]))

        # TAG
        tag_elem = soup.select(".breadcrumbs .breadcrumb a")
        if len(tag_elem) > 0:
            self.tag = tag_elem[-1].get_text(strip=True)

        # TITLE
        title_elem = soup.select_one(".tit")
        if title_elem is not None:
            self.title = title_elem.get_text(strip=True)

        # DROPHEAD
        drophead_elem = soup.select_one(".baj")
        if drophead_elem is not None:
            drophead_html = drophead_elem.decode_contents(formatter="html")
            self.drophead = self.parser.handle(drophead_html).strip()

        # EXCERPT
        # BODY
        body_elem = soup.select_one(".CUERPO")
        if body_elem is not None:
            for elem in body_elem.find_all("iframe"):
                elem.decompose()
            for elem in body_elem.find_all("script"):
                elem.decompose()
            for elem in body_elem.find_all("blockquote"):
                elem.decompose()
            for elem in body_elem.find_all("div", class_="prontus-card-container"):
                elem.decompose()

            body_html = body_elem.decode_contents(formatter="html")
            self.body = self.parser.handle(body_html).strip()
            self.bodyHTML = body_html
