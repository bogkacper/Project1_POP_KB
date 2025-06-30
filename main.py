from tkinter import *
import tkintermapview
import requests
from bs4 import BeautifulSoup

root = Tk()
root.geometry("1400x800")
root.title("mapbook_KACPERBOGUSZ")

# Map widget
map_widget = tkintermapview.TkinterMapView(root, width=900, height=700, corner_radius=0)
map_widget.grid(row=0, column=1, rowspan=999)
map_widget.set_position(52.23, 21.0)
map_widget.set_zoom(6)

# Left control frame
frame = Frame(root)
frame.grid(row=0, column=0, sticky=N, padx=10, pady=10)

# Input fields
Label(frame, text="Nazwa").grid(row=0, column=0)
entry_name = Entry(frame)
entry_name.grid(row=0, column=1)

Label(frame, text="Miejscowość").grid(row=1, column=0)
entry_location = Entry(frame)
entry_location.grid(row=1, column=1)

Label(frame, text="Cmentarz (jeśli dotyczy)").grid(row=2, column=0)
entry_cmentarz = Entry(frame)
entry_cmentarz.grid(row=2, column=1)

# Listboxes
listbox_cmentarzy = Listbox(frame, height=8, width=40)
listbox_pracownicy = Listbox(frame, height=8, width=40)
listbox_klienci = Listbox(frame, height=8, width=40)

listbox_cmentarzy.grid(row=5, column=0, columnspan=2, pady=5)
listbox_pracownicy.grid(row=7, column=0, columnspan=2, pady=5)
listbox_klienci.grid(row=9, column=0, columnspan=2, pady=5)

Label(frame, text="Cmentarze").grid(row=4, column=0)
Label(frame, text="Pracownicy").grid(row=6, column=0)
Label(frame, text="Klienci").grid(row=8, column=0)

# Button frames
frame_buttons_main = Frame(frame)
frame_buttons_main.grid(row=3, column=0, columnspan=2, pady=10)
frame_buttons_map = Frame(frame)
frame_buttons_map.grid(row=10, column=0, columnspan=2, pady=10)

# Data storage
obiekty = []
tryb_edycji = None
edycja_index = None

# Object class
class Obiekt:
    def __init__(self, typ, nazwa, miejscowosc, cmentarz=None):
        self.typ = typ
        self.nazwa = nazwa
        self.miejscowosc = miejscowosc
        self.cmentarz = cmentarz
        self.coordinates = self.get_coordinates()
        self.marker = map_widget.set_marker(self.coordinates[0], self.coordinates[1], text=nazwa)

    def get_coordinates(self):
        # First, try OpenStreetMap Nominatim geocoding for reliability
        try:
            resp = requests.get("https://nominatim.openstreetmap.org/search", params={
                'q': self.miejscowosc,
                'format': 'json',
                'limit': 1
            }, headers={'User-Agent': 'TkinterMapApp/1.0'})
            data = resp.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return [lat, lon]
        except Exception:
            pass
        # Fallback to Wikipedia parsing
        try:
            url = f"https://pl.wikipedia.org/wiki/{self.miejscowosc}"
            response = requests.get(url).text
            soup = BeautifulSoup(response, "html.parser")
            lat_e = soup.select(".latitude")
            lon_e = soup.select(".longitude")
            if lat_e and lon_e:
                lat = float(lat_e[0].text.replace(",", "."))
                lon = float(lon_e[0].text.replace(",", "."))
                return [lat, lon]
        except Exception:
            pass
        # Default to Warsaw
        return [52.23, 21.0]

# Label formatter
def format_etykiety(obiekt):
    if obiekt.typ == "cmentarz":
        return f"[Cmentarz] {obiekt.nazwa} ({obiekt.miejscowosc})"
    elif obiekt.typ == "pracownik":
        nr = sum(1 for o in obiekty if o.typ == "pracownik" and o.cmentarz == obiekt.cmentarz and obiekty.index(o) <= obiekty.index(obiekt))
        return f"[Pracownik {nr}] {obiekt.nazwa} ({obiekt.miejscowosc}) w {obiekt.cmentarz}"
    elif obiekt.typ == "klient":
        return f"[Klient] {obiekt.nazwa} ({obiekt.miejscowosc}) w {obiekt.cmentarz}"

# Refresh lists
def odswiez_listy():
    listbox_cmentarzy.delete(0, END)
    listbox_pracownicy.delete(0, END)
    listbox_klienci.delete(0, END)
    for ob in obiekty:
        if ob.typ == "cmentarz":
            listbox_cmentarzy.insert(END, format_etykiety(ob))
        elif ob.typ == "pracownik":
            listbox_pracownicy.insert(END, format_etykiety(ob))
        elif ob.typ == "klient":
            listbox_klienci.insert(END, format_etykiety(ob))

# Add object
def dodaj_obiekt(typ):
    global tryb_edycji, edycja_index
    nazwa = entry_name.get()
    miejscowosc = entry_location.get()
    cmentarz = entry_cmentarz.get()
    if nazwa and miejscowosc:
        if tryb_edycji:
            stary = obiekty[edycja_index]
            stary.marker.delete()
            obiekty[edycja_index] = Obiekt(typ, nazwa, miejscowosc, cmentarz or None)
            tryb_edycji = None
            edycja_index = None
            btn_edit.config(text="Aktualizuj zaznaczony")
        else:
            obiekty.append(Obiekt(typ, nazwa, miejscowosc, cmentarz or None))
        entry_name.delete(0, END)
        entry_location.delete(0, END)
        entry_cmentarz.delete(0, END)
        odswiez_listy()

# Delete object
def usun_obiekt():
    sel = None
    if listbox_cmentarzy.curselection(): sel = ("cmentarz", listbox_cmentarzy.curselection()[0])
    elif listbox_pracownicy.curselection(): sel = ("pracownik", listbox_pracownicy.curselection()[0])
    elif listbox_klienci.curselection(): sel = ("klient", listbox_klienci.curselection()[0])
    if sel:
        typ, idx = sel
        count = -1
        for i, ob in enumerate(obiekty):
            if ob.typ == typ:
                count += 1
            if count == idx:
                ob.marker.delete()
                obiekty.pop(i)
                break
        odswiez_listy()

# Edit object
def edytuj_obiekt():
    global tryb_edycji, edycja_index
    sel = None
    if listbox_cmentarzy.curselection(): sel = ("cmentarz", listbox_cmentarzy.curselection()[0])
    elif listbox_pracownicy.curselection(): sel = ("pracownik", listbox_pracownicy.curselection()[0])
    elif listbox_klienci.curselection(): sel = ("klient", listbox_klienci.curselection()[0])
    if sel:
        typ, idx = sel
        count = -1
        for i, ob in enumerate(obiekty):
            if ob.typ == typ:
                count += 1
            if count == idx:
                entry_name.delete(0, END)
                entry_name.insert(0, ob.nazwa)
                entry_location.delete(0, END)
                entry_location.insert(0, ob.miejscowosc)
                entry_cmentarz.delete(0, END)
                entry_cmentarz.insert(0, ob.cmentarz or "")
                tryb_edycji = typ
                edycja_index = i
                btn_edit.config(text="Zapisz zmiany")
                break

# Map views
def show_all_cmentarze():
    map_widget.delete_all_marker()
    for ob in obiekty:
        if ob.typ == "cmentarz":
            map_widget.set_marker(*ob.coordinates, text=ob.nazwa)

def show_all_pracownicy():
    map_widget.delete_all_marker()
    for ob in obiekty:
        if ob.typ == "pracownik":
            map_widget.set_marker(*ob.coordinates, text=ob.nazwa)

def show_klienci_for_selected():
    sel = listbox_cmentarzy.curselection()
    if not sel: return
    name = listbox_cmentarzy.get(sel[0]).split('] ')[1].split(' (')[0]
    map_widget.delete_all_marker()
    for ob in obiekty:
        if ob.typ == "klient" and ob.cmentarz == name:
            map_widget.set_marker(*ob.coordinates, text=ob.nazwa)

def show_pracownicy_for_selected():
    sel = listbox_cmentarzy.curselection()
    if not sel: return
    name = listbox_cmentarzy.get(sel[0]).split('] ')[1].split(' (')[0]
    map_widget.delete_all_marker()
    for ob in obiekty:
        if ob.typ == "pracownik" and ob.cmentarz == name:
            map_widget.set_marker(*ob.coordinates, text=ob.nazwa)

# Buttons main
btn_add_cmentarz = Button(frame_buttons_main, text="Dodaj cmentarz", width=20, command=lambda: dodaj_obiekt("cmentarz"))
btn_add_pracownik = Button(frame_buttons_main, text="Dodaj pracownika", width=20, command=lambda: dodaj_obiekt("pracownik"))
btn_add_klient = Button(frame_buttons_main, text="Dodaj klienta", width=20, command=lambda: dodaj_obiekt("klient"))
btn_edit = Button(frame_buttons_main, text="Aktualizuj zaznaczony", width=20, command=edytuj_obiekt)
btn_delete = Button(frame_buttons_main, text="Usuń zaznaczony", width=20, command=usun_obiekt)

btn_add_cmentarz.grid(row=0, column=0, padx=5, pady=5)
btn_add_pracownik.grid(row=0, column=1, padx=5, pady=5)
btn_add_klient.grid(row=0, column=2, padx=5, pady=5)
btn_edit.grid(row=1, column=0, padx=5, pady=5)
btn_delete.grid(row=1, column=1, padx=5, pady=5)

# Buttons map
btn_show_cmentarze = Button(frame_buttons_map, text="Mapa wszystkich cmentarzy", width=25, command=show_all_cmentarze)
btn_show_pracownicy = Button(frame_buttons_map, text="Mapa wszystkich pracowników", width=25, command=show_all_pracownicy)
btn_show_klienci = Button(frame_buttons_map, text="Mapa klientów wybranego cmentarza", width=34, command=show_klienci_for_selected)
btn_show_prac_c = Button(frame_buttons_map, text="Mapa pracowników wybranego cmentarza", width=34, command=show_pracownicy_for_selected)

btn_show_cmentarze.grid(row=0, column=0, pady=2)
btn_show_pracownicy.grid(row=1, column=0, pady=2)
btn_show_klienci.grid(row=2, column=0, pady=2)
btn_show_prac_c.grid(row=3, column=0, pady=2)

# Initialize lists and default view
odswiez_listy()
show_all_cmentarze()

root.mainloop()
