import argparse

from kurek.user import User


parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description = """
         oooo    oooo ooooo     ooo ooooooooo.   oooooooooooo oooo    oooo
         `888   .8P'  `888'     `8' `888   `Y88. `888'     `8 `888   .8P'
          888  d8'     888       8   888   .d88'  888          888  d8'
          88888[       888       8   888ooo88P'   888oooo8     88888[
          888`88b.     888       8   888`88b.     888    "     888`88b.
          888  `88b.   `88.    .8'   888  `88b.   888       o  888  `88b.
         o888o  o888o    `YbodP'    o888o  o888o o888ooooood8 o888o  o888o

    Pobierz media z profilów na zbiornik.com

    Skrypt pozwala na masowe pobieranie zdjęć i filmów profilów zarejestrowanych
    na zbiornik.com.
    Używa bibliotek opartych na asyncio, dzięki czemu media pobierane są
    bardzo szybko i równolegle. Wymagane jest konto na portalu. Media pobierane
    są w jakości zależnej od statusu konta użytkownika.
    """,
    epilog = """
    Używaj odpowiedzialnie!
    """
)

parser.add_argument('-u', '--email',
                    nargs=1,
                    type=str,
                    metavar='EMAIL',
                    required=True,
                    help='email użytkownika')
parser.add_argument('-p', '--pass',
                    dest='password',
                    nargs=1,
                    type=str,
                    metavar='PASSWORD',
                    required=True,
                    help='hasło użytkownika')
parser.add_argument('profiles',
                    nargs='*',
                    type=str,
                    metavar='PROFILE',
                    help="nazwa profilu do ściągnięcia")
parser.add_argument('-f', '--file',
                    nargs=1,
                    type=str,
                    metavar='FILE',
                    help="Plik z listą nazw profilów")

args = parser.parse_args()
if not args.profiles and not args.file:
    parser.error("podaj nazwy profilów lub ścieżkę do pliku za pomocą --file")

user = User(args.email, args.password)
user.login()
