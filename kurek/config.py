# Copyright (C) Bartosz Bartyzel 2022
# Distributed under the MIT License.
# License terms are at https://opensource.org/licenses/MIT and in LICENSE.md

import os


host = 'zbiornik.com'
scheme = 'https'
api_servers = ('dzesika', 'brajanek', 'vaneska', 'denisek')
api_root = '/ajax/'
request_headers = {
    'User-Agent': 'Mozilla/5.0',
}
max_server_requests = 5
max_download_requests = 10
max_api_requests = 50
only_photos = False
only_videos = False
save_dir = 'profiles'
save_template = os.path.join('%d', '%p', '%t')
name_template = '%t-%h.%e'
