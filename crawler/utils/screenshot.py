import asyncio
import os
from io import BytesIO  # Import BytesIO to handle in-memory bytes data

from PIL import Image
from playwright.async_api import Page


async def scroll_and_capture(
    page: Page,
    path: str,
    sleep_time: int = 1,
    remove_header: bool = True,
    remove_footer: bool = False,
    save_tmp: bool = False,
    viewport_height_adjustment: int = 0,
):
    tmp_path = 'tmp'

    header_selector = 'div.header'
    header_height = await page.evaluate(f"""
        () => {{
            const header = document.querySelector('{header_selector}');
            if (header && header.style.display !== 'none' && header.offsetHeight > 0) {{
                return header.offsetHeight;
            }}
            return 0;
        }}
    """)

    footer_selector = 'div.hyl-comment-foot__fixed'
    footer_height = await page.evaluate(f"""
        () => {{
            const footer = document.querySelector('{footer_selector}');
            if (footer && footer.style.display !== 'none' && footer.offsetHeight > 0) {{
                return footer.offsetHeight;
            }}
            return 0;
        }}
    """)

    scrollable_selector = 'div.root__scroll-body'
    viewport_height = await page.evaluate(
        f"document.querySelector('{scrollable_selector}').clientHeight"
    )
    viewport_height = int(viewport_height) + viewport_height_adjustment
    screenshot_count = 0

    images = []

    if save_tmp:
        os.makedirs(tmp_path, exist_ok=True)

    # the first screenshot
    scroll_top = 0
    screenshot_data = await page.screenshot(full_page=True)
    screenshot = Image.open(BytesIO(screenshot_data))
    box = (0, 0, screenshot.width, screenshot.height)
    # the first screenshot does not need to remove header
    # if remove_header:
    #     box = (box[0], box[1] + header_height, box[2], box[3])
    if remove_footer:
        box = (box[0], box[1], box[2], box[3] - footer_height)
    screenshot = screenshot.crop(box)
    if save_tmp:
        screenshot.save(os.path.join(tmp_path, f'{screenshot_count:04d}.png'))
    images.append(screenshot)
    screenshot_count += 1

    while True:
        pre_scroll_top = scroll_top
        # slide a viewport height to the bottom
        await page.evaluate(f"""
                        const scrollableDiv = document.querySelector('{scrollable_selector}');
                        if (scrollableDiv) {{
                            scrollableDiv.scrollTop += {viewport_height};
                        }}
                    """)
        await asyncio.sleep(sleep_time)

        scroll_top = await page.evaluate(
            f"document.querySelector('{scrollable_selector}').scrollTop"
        )

        if scroll_top - pre_scroll_top == viewport_height:
            screenshot_data = await page.screenshot(full_page=True)
            screenshot = Image.open(BytesIO(screenshot_data))
            box = (0, 0, screenshot.width, screenshot.height)
            if remove_header:
                box = (box[0], box[1] + header_height, box[2], box[3])
            if remove_footer:
                box = (box[0], box[1], box[2], box[3] - footer_height)
            screenshot = screenshot.crop(box)
            images.append(screenshot)
            if save_tmp:
                screenshot.save(os.path.join(tmp_path, f'{screenshot_count:04d}.png'))

            screenshot_count += 1
        elif scroll_top - pre_scroll_top < viewport_height:
            # last screenshot
            screenshot_data = await page.screenshot(full_page=False)
            screenshot = Image.open(BytesIO(screenshot_data))
            box = (
                0,
                viewport_height - (scroll_top - pre_scroll_top),
                screenshot.width,
                screenshot.height,
            )
            if remove_header:
                box = (box[0], box[1] + header_height, box[2], box[3])
            if remove_footer:
                box = (box[0], box[1], box[2], box[3] - footer_height)
            screenshot = screenshot.crop(box)
            images.append(screenshot)

            if save_tmp:
                screenshot.save(os.path.join(tmp_path, f'{screenshot_count:04d}.png'))
            break

    # scroll to the top
    await page.evaluate(
        f"document.querySelector('{scrollable_selector}').scrollTop = 0"
    )

    combine_screenshots_in_memory(images, path)


def combine_screenshots_in_memory(images, output_file):
    widths, heights = zip(*(img.size for img in images))
    total_height = sum(heights)

    combined_image = Image.new('RGB', (widths[0], total_height))

    y_offset = 0
    for img in images:
        combined_image.paste(img, (0, y_offset))
        y_offset += img.size[1]

    combined_image.save(output_file)
