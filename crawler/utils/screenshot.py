import time
from io import BytesIO  # Import BytesIO to handle in-memory bytes data

from PIL import Image
from playwright.async_api import Page


async def move_to_header(page: Page):
    header_selector = 'div.header'
    await page.evaluate(f"""
        const header = document.querySelector('{header_selector}');
        if (header) {{
            const rect = header.getBoundingClientRect(); // Get the header's position and dimensions
            const mouseEvent = new MouseEvent('mousemove', {{
                clientX: rect.left + rect.width / 2, // Horizontal center of the header
                clientY: rect.top + rect.height / 2,  // Vertical center of the header
                bubbles: true, // Ensure the event propagates
                cancelable: true
            }});
            document.dispatchEvent(mouseEvent); // Dispatch the mousemove event
            console.log('Mouse moved to header');
        }} else {{
            console.log('Header not found');
        }}
    """)


async def scroll_and_capture(page: Page, path: str):
    header_selector = 'div.header'

    header_height = await page.evaluate(f"""
                const header = document.querySelector('{header_selector}');
                header ? header.offsetHeight : 0;
            """)

    scrollable_selector = 'div.root__scroll-body.sr-banner-style'
    viewport_height = await page.evaluate(
        f"document.querySelector('{scrollable_selector}').clientHeight"
    )
    screenshot_count = 0

    images = []

    # the first screenshot
    scroll_top = 0
    await move_to_header(page)
    screenshot_data = await page.screenshot(full_page=False)
    screenshot = Image.open(BytesIO(screenshot_data))
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
        time.sleep(1)

        scroll_top = await page.evaluate(
            f"document.querySelector('{scrollable_selector}').scrollTop"
        )

        if scroll_top - pre_scroll_top == viewport_height:
            await move_to_header(page)
            screenshot_data = await page.screenshot(full_page=False)
            screenshot = Image.open(BytesIO(screenshot_data))
            screenshot = screenshot.crop(
                (0, header_height, screenshot.width, screenshot.height)
            )
            images.append(screenshot)

            screenshot_count += 1
        elif scroll_top - pre_scroll_top < viewport_height:
            # last screenshot

            await move_to_header(page)
            screenshot_data = await page.screenshot(full_page=False)
            screenshot = Image.open(BytesIO(screenshot_data))
            screenshot = screenshot.crop(
                (
                    0,
                    viewport_height - (scroll_top - pre_scroll_top) + header_height,
                    screenshot.width,
                    screenshot.height,
                )
            )
            images.append(screenshot)
            break

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
