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
                        type=str,
                        metavar='EMAIL',
                        required=True,
                        help='email użytkownika')
    parser.add_argument('-p',
                        '--pass',
                        dest='password',
                        type=str,
                        metavar='PASSWORD',
                        required=True,
                        help='hasło użytkownika')
    parser.add_argument('-f',
                        '--file',
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
                        type=str,
                        default=config.save_dir,
                        metavar='DIR',
                        help=f'folder zapisu')
    parser.add_argument('-t',
                        '--dir-template',
                        dest='save_template',
                        type=str,
                        default=config.save_template,
                        metavar='STR',
                        help='''wzorzec ścieżki zapisu:
    %%d - root dir
    %%p - nazwa profilu
    %%t - typ pliku (photo/video)
''')
    parser.add_argument('-n',
                        '--filename-template',
                        dest='name_template',
                        type=str,
                        default=config.name_template,
                        metavar='STR',
                        help='''wzorzec nazwy pliku:
    %%t - tytuł
    %%h - unikatowy hash pliku
    %%e - rozszerzenie
    %%o - nazwa właściciela
    %%d - opis

    Puste stringi zamieniane są na '_'.
''')
    parser.add_argument('-a',
                        '--api-limit',
                        type=int,
                        default=config.max_api_requests,
                        metavar='INT',
                        help='limit zapytań API')
    parser.add_argument('-l',
                        '--download-limit',
                        type=int,
                        default=config.max_download_requests,
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
        with open(args.file, 'r') as file:
            file_profiles = file.read().splitlines()
            if not file_profiles:
                parser.error(f'plik {args.file} jest pusty')
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

if __name__ == '__main__':
    asyncio.run(main())
