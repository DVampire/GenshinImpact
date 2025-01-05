import os

from crawler.utils.html_files import save_html_file


async def save_element_overleaf(
    page, element, save_name, img_path, html_path, set_height_scale
):  # type: ignore
    """Save the screenshot of an element to a file"""
    original_viewport_size = page.viewport_size

    set_size = {
        'width': original_viewport_size['width'],
        'height': int(original_viewport_size['height'] * set_height_scale),
    }
    await page.set_viewport_size(set_size)

    image = await element.screenshot()

    img_path = os.path.join(img_path, f'{save_name}.png')
    with open(img_path, 'wb') as file:
        file.write(image)

    # Get the inner HTML of the element
    content = await element.evaluate('el => el.outerHTML')

    # Save the HTML content to a file
    html_path = os.path.join(html_path, f'{save_name}.html')
    save_html_file(content, html_path)

    await page.set_viewport_size(original_viewport_size)

    return content, img_path, html_path


async def save_element(element, save_name, img_path, html_path):  # type: ignore
    """Save the screenshot of an element to a file"""

    image = await element.screenshot()

    img_path = os.path.join(img_path, f'{save_name}.png')
    with open(img_path, 'wb') as file:
        file.write(image)

    # Get the inner HTML of the element
    content = await element.evaluate('el => el.outerHTML')

    # Save the HTML content to a file
    html_path = os.path.join(html_path, f'{save_name}.html')
    save_html_file(content, html_path)

    return content, img_path, html_path
