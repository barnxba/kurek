import argparse
import asyncio
import logging

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

Pobierz media z profilów na zbiornik.com

Skrypt pozwala na masowe pobieranie zdjęć i filmów z kont zarejestrowanych
na zbiornik.com.
Używa bibliotek opartych na asyncio, dzięki czemu media pobierane są
bardzo szybko i równolegle. Wymagane jest konto na portalu. Media pobierane
są w jakości zależnej od statusu konta użytkownika.
        ''',
        epilog = '''
Używaj odpowiedzialnie!
        '''
    )

    parser.add_argument('-u',
                        '--email',
                        nargs=1,
                        type=str,
                        metavar='EMAIL',
                        required=True,
                        help='email użytkownika')
    parser.add_argument('-p',
                        '--pass',
                        dest='password',
                        nargs=1,
                        type=str,
                        metavar='PASSWORD',
                        required=True,
                        help='hasło użytkownika')
    parser.add_argument('-f',
                        '--file',
                        nargs=1,
                        type=str,
                        metavar='FILE',
                        help='plik z listą nazw profilów')
    exclude_media = parser.add_mutually_exclusive_group()
    exclude_media.add_argument('-g',
                               '--gallery',
                               dest='only_photos',
                               action='store_true',
                               help='ściągnij tylko zdjęcia')
    exclude_media.add_argument('-v',
                               '--videos',
                               dest='only_videos',
                               action='store_true',
                               help='ściągnij tylko filmy')
    parser.add_argument('-d',
                        '--root-dir',
                        dest='save_dir',
                        nargs=1,
                        type=str,
                        metavar='DIR',
                        help=f'folder zapisu ("{config.save_dir}")')
    parser.add_argument('-t',
                        '--dir-template',
                        dest='save_template',
                        nargs=1,
                        type=str,
                        metavar='TEMPLATE',
                        help='''wzorzec ścieżki zapisu [%%d/%%p/%%t]):
    %%d - root dir
    %%p - nazwa profilu
    %%t - typ pliku (photo/video)
''')
    parser.add_argument('-n',
                        '--filename-template',
                        dest='name_template',
                        nargs=1,
                        type=str,
                        metavar='TEMPLATE',
                        help='''wzorzec nazwy pliku [%%t_%%h.%%e]):
    %%t - tytuł
    %%h - unikatowy hash pliku
    %%e - rozszerzenie
    %%o - nazwa właściciela
    %%d - opis

    Puste stringi zamieniane są znakiem '_'.
''')
    parser.add_argument('-a',
                        '--api-limit',
                        nargs=1,
                        type=int,
                        metavar='INT',
                        help='limit zapytań API')
    parser.add_argument('-l',
                        '--download-limit',
                        nargs=1,
                        type=int,
                        metavar='INT',
                        help='limit jednoczesnych pobrań')
    parser.add_argument('profiles',
                        nargs='*',
                        type=str,
                        metavar='PROFILE',
                        help='nazwa profilu do ściągnięcia')

    args = parser.parse_args()
    if not args.profiles and not args.file:
        parser.error('podaj nazwy profilów lub użyj opcji --file')

    # consolidate profile names
    file_profiles = []
    if args.file:
        filename = args.file[0]
        with open(filename, 'r') as file:
            file_profiles = file.read().splitlines()
            if not file_profiles:
                parser.error(f'plik {filename} jest pusty')
    profiles = sorted([*args.profiles, *file_profiles],
                      key=lambda s: s.lower())

    logging.basicConfig()
    log = logging.getLogger('main')

    config.only_photos = args.only_photos
    config.only_videos = args.only_videos
    if args.save_dir:
        config.save_dir = args.save_dir[0]
    if args.save_template:
        config.save_template = args.save_template[0]
    if args.name_template:
        config.name_template = args.name_template[0]
    if args.api_limit:
        config.max_api_requests = args.api_limit[0]
    if args.download_limit:
        config.max_download_requests = args.download_limit[0]

    log.debug(f'Run parameters:')
    log.debug(f'\tonly_photos: {config.only_photos}')
    log.debug(f'\tonly_videos: {config.only_videos}')
    log.debug(f'\tsave_dir: {config.save_dir}')
    log.debug(f'\tsave_template: {config.save_template}')
    log.debug(f'\tname_template: {config.name_template}')
    log.debug(f'\download_limit: {config.max_download_requests}')
    log.debug(f'\tapi_limit: {config.max_api_requests}')

    session = Session(config.max_api_requests,
                      config.max_download_requests,
                      config.request_headers)
    await session.start()
    await session.login(args.email[0], args.password[0])
    await asyncio.gather(*(Profile(nick).download(session) for nick in profiles))
    await session.close()

if __name__ == '__main__':
    asyncio.run(main())
