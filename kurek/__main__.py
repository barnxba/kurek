# Copyright (C) Bartosz Bartyzel 2022
# Distributed under the MIT License.
# License terms are at https://opensource.org/licenses/MIT and in LICENSE.md

import asyncio
import argparse

from kurek import config
from kurek.session import Session
from kurek.profile import Profile


async def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description = '''
    oooo    oooo ooooo     ooo ooooooooo.   oooooooooooo oooo    oooo
    `888   .8P'  `888'     `8' `888   `Y88. `888'     `8 `888   .8P'
    888  d8'     888       8   888   .d88'  888          888  d8'
    88888[       888       8   888ooo88P'   888oooo8     88888[
    888`88b.     888       8   888`88b.     888    "     888`88b.
    888  `88b.   `88.    .8'   888  `88b.   888       o  888  `88b.
    o888o  o888o    `YbodP'    o888o  o888o o888ooooood8 o888o  o888o

Batch media downloader for zbiornik.com

This script is used to download photos and videos of profiles registered on
zbiornik.com.
It uses libraries based on *asyncio* to rapidly download data - tasks are run
concurrently so that saving massive amounts of data is very fast.
A registered account on the site is required. Media quality is based on account
status. Only the highest fidelity.
        ''',
        epilog = '''
Use responsibly! Use download and API limits. Live and let live.
        '''
    )

    parser.add_argument('-u',
                        '--email',
                        type=str,
                        metavar='EMAIL',
                        required=True,
                        help='login email')
    parser.add_argument('-p',
                        '--pass',
                        dest='password',
                        type=str,
                        metavar='PASSWORD',
                        required=True,
                        help='login password')
    parser.add_argument('-f',
                        '--file',
                        type=str,
                        metavar='FILE',
                        help='file with a list of profile names (1 name/line)')
    exclude_media = parser.add_mutually_exclusive_group()
    exclude_media.add_argument('-g',
                               '--gallery',
                               dest='only_photos',
                               action='store_true',
                               help='download photos only')
    exclude_media.add_argument('-v',
                               '--videos',
                               dest='only_videos',
                               action='store_true',
                               help='download videos only')
    parser.add_argument('-d',
                        '--root-dir',
                        dest='save_dir',
                        type=str,
                        default=config.save_dir,
                        metavar='DIR',
                        help=f'base folder to save data to')
    parser.add_argument('-t',
                        '--dir-template',
                        dest='save_template',
                        type=str,
                        default=config.save_template,
                        metavar='STR',
                        help='''save path template:
    %%d - base directory
    %%p - profile name
    %%t - file type (photo/video)
''')
    parser.add_argument('-n',
                        '--filename-template',
                        dest='name_template',
                        type=str,
                        default=config.name_template,
                        metavar='STR',
                        help='''name template for files:
    %%t - title
    %%h - unique hash ID
    %%e - file extension
    %%o - owner's profile name
    %%d - description

    Empty strings are replaced with '_'.
''')
    parser.add_argument('-a',
                        '--api-limit',
                        type=int,
                        default=config.max_api_requests,
                        metavar='INT',
                        help='API requests limit')
    parser.add_argument('-l',
                        '--download-limit',
                        type=int,
                        default=config.max_download_requests,
                        metavar='INT',
                        help='simultaneous downloads limit')
    parser.add_argument('profiles',
                        nargs='*',
                        type=str,
                        metavar='PROFILE',
                        help='list of profile names')

    args = parser.parse_args()
    if not args.profiles and not args.file:
        parser.error('no profile names given')

    # consolidate profile names
    file_profiles = []
    if args.file:
        with open(args.file, 'r') as file:
            file_profiles = file.read().splitlines()
            if not file_profiles:
                parser.error(f'file {args.file} is empty')
    profiles = sorted([*args.profiles, *file_profiles],
                      key=lambda s: s.lower())

    config.only_photos = args.only_photos
    config.only_videos = args.only_videos
    if args.save_dir:
        config.save_dir = args.save_dir
    if args.save_template:
        config.save_template = args.save_template
    if args.name_template:
        config.name_template = args.name_template
    if args.api_limit:
        config.max_api_requests = args.api_limit
    if args.download_limit:
        config.max_download_requests = args.download_limit

    email, password = args.email, args.password

    session = Session(config.max_api_requests,
                      config.max_download_requests,
                      config.request_headers)
    await session.start()
    await session.login(email, password)
    await asyncio.gather(*(Profile(nick).download(session) for nick in profiles))
    await session.close()

def run():
    asyncio.run(main())

if __name__ == '__main__':
    run()
