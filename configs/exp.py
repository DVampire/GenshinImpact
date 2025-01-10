workdir = 'workdir'
platform = 'genshin_impact'
tag = platform
exp_path = f'{workdir}/{tag}'
html_path = f'{exp_path}/html'
img_path = f'{exp_path}/img'

# proxy
enable_ip_proxy = False
ip_proxy_pool_count = 2

# browser
headless = False
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
save_login_state = True
save_data_option = 'json'
user_data_dir = f'{platform}_user_data'

# parser
batch_size = 1
save_screen = False
set_width_scale = 1.0
set_height_scale = 4.0
