import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from datetime import datetime, date

import pandas as pd

from scrapedata import scrape_data_from_GOG
from sqlitedb import insert_into_games, insert_into_prices, create_table, select_data, try_execute_sql, if_record_exist

import os
from dotenv import load_dotenv

load_dotenv()
dbname = os.getenv('DBNAME')


def split_columns_names(columns: list):
    tmp = list()

    for name in columns:
        tmp.append(name.replace("_", " ").capitalize())

    return tmp


class App(tk.Tk):
    def __init__(self):
        super(App, self).__init__()

        self.title("Aplikacja")
        # W jakiś sposób muszę zmieniać rozmiar elementów w środku apki wraz z zmianą okna - Może CANVAS?
        self.minsize(1250, 350)
        self.maxsize(1920, 1080)

        self.crate_db_if_not_exists()

        self.check_prices()

        self.creating_window()
        self.grid()

    def masseges(self, title: str, message: str):
        """
        Metoda do wyietlania komunikatów???
        :return:
        """
        messagebox.showinfo(title, message)


    def refresh_prices(self):
        """
        Zastanowić się nad lepszą nazwą...
        Metoda do ręcznego odświeżania cen gier
        :return:
        """

        sql = """
            SELECT g.id, g.link
            FROM games AS g
            GROUP BY g.link
            ORDER BY g.id;
        """

        links = select_data(sql)

        links = pd.DataFrame(links[1], columns=links[0]).values.tolist()

        print(links)

        for _, link in links:
            game_data = scrape_data_from_GOG(str(link))
            insert_into_prices(game_data)

    def check_prices(self):
        """
        Nazwa jeszcze do przemyślenia
        Wraz z startem apki potrzebny jest system do aktualizacji cen
        Jeżeli aktualizacja była robiona danego dnia to nie ma potrzeby robić jej ponownie
        :return:
        """

        sql = """
            SELECT g.link, MAX(datetime(p.checked_date, 'localtime')) AS checked
            FROM prices AS p
            INNER JOIN games AS g ON p.game_id = g.id
            GROUP BY g.link
            ORDER BY checked DESC;
        """

        data = select_data(sql)

        data = pd.DataFrame(data[1], columns=data[0]).values.tolist()

        for link, last_check_date in data:
            last_check_date = datetime.strptime(last_check_date, '%Y-%m-%d %H:%M:%S').date()
            today = date.today()

            if last_check_date != today:
                game_data = scrape_data_from_GOG(str(link))
                insert_into_prices(game_data)
            else:
                print(f"Gra {link} była już dziś aktualizowana przy starcie.")

    def display_data(self):
        """
            Metoda do wyświetlenia danych w oknie aplikacji
        """

        # Myślę, że będzie trzeba dopisać do tego jakiś przycisk odśwież.

        sql = """
            SELECT g.title, g.release, datetime(g.added, 'localtime') AS added, p.base_price, p.currency
            FROM games AS g
            INNER JOIN prices AS p ON g.id = p.game_id
            GROUP BY g.title
            ORDER BY g.title;
        """

        columns, data = select_data(sql)
        columns = split_columns_names(columns)

        return columns, data

    def crate_db_if_not_exists(self):
        if not os.path.exists(dbname):
            create_table()

    def add_site(self):
        """
            Metoda odpowiedzialna za wyciągnięcie z panelu wprowadzania strony i odpalenia funkcji do wydobycia z niej
            danych.
        """
        website = self.enter_site_entry.get()

        gama_data = scrape_data_from_GOG(str(website))

        if if_record_exist(gama_data):
            self.masseges("Rekord istnieje", f"Gra {gama_data['title']} jest już w bazie danych.")
        else:
            insert_into_games(gama_data)
            insert_into_prices(gama_data)
            self.add_new_row_to_tree_view(gama_data)

    def add_new_row_to_tree_view(self, data):
        sql = """
            SELECT g.title, g.release, datetime(g.added, 'localtime') AS added, p.base_price, p.currency
            FROM games AS g
            INNER JOIN prices AS p ON g.id = p.game_id
            WHERE g.title = ? OR g.title LIKE ?;
        """

        row = try_execute_sql(sql, (data['title'], data['title']))

        for value in row:
            self.tree.insert('', tk.END, values=value)

    def stop_updates(self):
        """
            Wstrzymanie aktualizacji cen danej produkcji ale zostawienie jej w "głównej tabeli".
        """
        pass

    def remove_site(self):
        """
            Funkcja podpięta do przycisku znajdującego się na końcu tabeli.
            Służy do usunięcia rekordu z "głównej tabeli" i wstrzymanie aktualizacji dla tej gry.
            Dane o grze i zebrane aktualizacje powinny zostać w plikach z danymi.
        """

    def bar_menu(self):
        pass

    # def on_resize(self, event):
    #     self.canvas.configure(width=event.width, height=event.height)

    def creating_window(self):
        """
            Metoda definiująca rozkład elementów w aplikacji.
        """

        # PŁÓTNO: ======================================================================================================

        # self.bind("<Configure>", self.on_resize)    # Ustawienie funkcji obsługującej zdarzenie zmiany rozmiaru okna
        #
        # self.canvas = tk.Canvas(self)
        # self.canvas.grid(row=0, column=0, padx=2, pady=2, ipadx=2, ipady=2, sticky='nsew')

        # WPROWADZANIE DANYCH: =========================================================================================

        enter_site_lf = tk.LabelFrame(self, text="Wprowadź stronę internetową:")
        enter_site_lf.grid(padx=2, pady=2, ipadx=2, ipady=2, sticky='ew')

        # Pole wprowadzania stron internetowych: -----------------------------------------------------------------------

        # USUWAĆ PO ZATWIERDZENIU POPRZEDNI STRING
        self.enter_site_entry = tk.Entry(enter_site_lf)
        self.enter_site_entry.grid(row=0, column=0, padx=2, pady=2, ipadx=2, ipady=2)

        # Przycisk zatwierdź: ------------------------------------------------------------------------------------------

        tk.Button(enter_site_lf, text="Zatwierdź", command=self.add_site)\
            .grid(row=0, column=1, padx=2, pady=2, ipadx=2, ipady=2)

        # Przycisk odśwież: --------------------------------------------------------------------------------------------
        # Muszę zmienić położenie tego przycisku. Może w pasku narzędzi?
        tk.Button(enter_site_lf, text="Odśwież", command=self.refresh_prices)\
            .grid(row=0, column=2, padx=2, pady=2, ipadx=2, ipady=2)

        # PASEK Z PRZYCISKAMI??? =======================================================================================

        # TABELA: ======================================================================================================

        table_lf = tk.LabelFrame(self, text="Tabela:")
        table_lf.grid(padx=2, pady=2, ipadx=2, ipady=2, sticky='ew')

        # Zdefiniowanie kolumn
        columns, data = self.display_data()

        self.tree = ttk.Treeview(table_lf, columns=columns, show='headings')

        # Zdefiniowanie nagłówków kolumn:

        for column_name in columns:
            self.tree.heading(column_name, text=column_name)

        # Wstawienie danych do tabeli:

        for row in data:
            self.tree.insert('', tk.END, values=row)

        self.tree.grid(row=0, column=0, padx=2, pady=2, ipadx=2, ipady=2, sticky='nsew')

        self.tree_y_scrollbnar = ttk.Scrollbar(table_lf, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=self.tree_y_scrollbnar.set)
        self.tree_y_scrollbnar.grid(row=0, column=1, padx=2, pady=2, ipadx=2, ipady=2, sticky='ns')

        self.tree_x_scrollbnar = ttk.Scrollbar(table_lf, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscroll=self.tree_x_scrollbnar.set)
        self.tree_x_scrollbnar.grid(row=1, column=0, columnspan=2, padx=2, pady=2, ipadx=2, ipady=2, sticky='ew')

    def run(self):
        self.mainloop()
