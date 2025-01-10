from typing import Any, Dict

from scrapy.selector import Selector

from crawler.utils.url import add_url


def get_item(td: Selector) -> Dict[str, Any] | str:
    ps = td.xpath('.//p')

    if not ps:
        return td.xpath('.//text()').get().strip()
    else:
        content = ''.join(td.xpath('.//text()').getall()).strip()
        items = []
        for p in ps:
            # if a element in the p element
            a = p.xpath('./a')
            if a:
                text = a.xpath('.//text()').get().strip()
                url = add_url(a.xpath('./@href').get().strip())
                items.append({'text': text, 'url': url})

            span = p.xpath('./span[@class="custom-entry-wrapper"]')
            if span:
                url = add_url(span.xpath('@data-entry-link').get().strip())
                text = span.xpath('@data-entry-name').get().strip()
                icon_url = span.xpath('@data-entry-img')
                if icon_url:
                    icon_url = add_url(icon_url.get().strip())
                    items.append({'text': text, 'url': url, 'icon_url': icon_url})
                else:
                    items.append({'text': text, 'url': url})

        if items:
            return {'content': content, 'items': items}
        else:
            return content
