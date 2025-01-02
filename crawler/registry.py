from mmengine.registry import Registry

LOGGER = Registry('logger', locations=['crawler.logger'])

CORE = Registry('core', locations=['crawler.core'])
