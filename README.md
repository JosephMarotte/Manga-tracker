# Manga-tracker
The aim of this project is to track manga on different website.
Provided a list of manga a list of manga with the last chapter read the program
should be able to retrieve whether there are new chapter to read for each of these
manga.

## Install

Our project use mysql database to store information so you need to install it

`sudo apt-get install mysql-server mysql-client`

If needed set MySQL root user password for the first time

`sudo mysqladmin -u root password NEWPASSWORD`

Connect to MySQL as root to setup a user for our program :

`sudo mysql -u root -p`

Create the user

`CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password'`

Grant authorization to the user

`GRANT ALL PRIVILEGES ON manga_tracker.* TO 'newuser'@'localhost'`

Install pip3

`sudo apt-get install python3-pip`

Install requirements

`pip3 install -r requirements.txt`

## Command line interface

The command line use [argparse](https://docs.python.org/3/library/argparse.html) library.
`python3 -m manga_tracker -h` shows the list of commands.

### `set_login_and_password` command

`python3 -m manga_tracker login password`
This command setup login and password to connect to the mysql database (you have to provide login and password you set up before)

### `create_user` command

`python3 -m manga_tracker [-v] create_user`
This command create a new user and prints its id.

### `change_language_pref_order` command

`python3 -m manga_tracker [-v] change_language_pref_order [-h] user_id language_pref_order [language_pref_order ...]`
This command change the ranking of the language preference for a user

### `change_website_pref_order` command

`python3 -m manga_tracker [-v] change_language_pref_order [-h] user_id website_pref_order [website_pref_order ...]`
This command change the ranking of the website preference for a user

### `add_followed_manga` command

`python3 -m manga_tracker [-v] add_followed_manga [-h] user_id title_or_manga_id [title_or_manga_id ...]`
This command add new followed manga to a user

### `retrieve_followed_manga` command

`python3 -m manga_tracker [-v] retrieve_followed_manga [-h] user_id output_file`
This command retrieve chapter of the user's followed manga and output it under a rss format to output_file

### `populate_dataset` command

`python3 -m manga_tracker [-v] populate_database [-h] [website_name_list [website_name_list ...]]`
This command retrieve new manga chapter on the given website.

## Execution example
- Set mysql login and password
`python3 -m manga_tracker login password`

- Retrieve manga and chapter from [Leviatanscans](https://leviatanscans.com/) and [Zeroscans](https://zeroscans.com/) websites

`python3 -m manga_tracker populate_database leviatanscans zeroscans`
- Create a new user

`python3 -m manga_tracker create_user` (assume the user_id is 24)
- Set languages preferences for this user

`python3 -m manga_tracker change_language_pref_order 24 eng fra` (this user prefer to read chapter in english than in french)
- Set website preferences for this user

`python3 -m manga_tracker change_website_pref_order 24 zeroscans leviatanscans` (this user prefer to read chapter on zeroscans than leviatanscans)
- Add manga followed by this user

`python3 -m manga_tracker add_followed_manga 24 'chronicles of heavenly demon' 'medical return' 'second life ranker'` (these three mangas are added to the list of the followed manga of the user)
- Retrieve chapter for this user

`python3 -m manga_tracker retrieve_followed_manga 24 chapters_i_have_to_read.xml`

