communal_cemeteries: list[dict] = [
    {'communal_cemeteries': 'MazurTrans', 'communal_cemeteries_location': 'Białystok'},
    {'communal_cemeteries': 'Rzymskokatolicki', 'communal_cemeteries_location': 'Bydgoszcz'},
    {'communal_cemeteries': 'Prawoslawny', 'communal_cemeteries_location': 'Kraków'},
    {'communal_cemeteries': 'Wolnosci', 'communal_cemeteries_location': 'Gdańsk'}
]

clients: list[dict] = [
    {'client_name': 'Ryszard Konieczny', 'client_communal_cemeteries': 'Krystyna Szulik', 'client_location1': 'Łapy', 'client_location2': 'Gdańsk'}
]

workers: list[dict] = [
    {'worker_name': 'Tomasz Oleszko', 'worker_communal_cemeteries': 'MazurTrans', 'worker_location': 'Sopot'},
    {'worker_name': 'Kuba Stalewski', 'worker_communal_cemeteries': 'Katowice', 'worker_location': 'Szczecin'},
    {'worker_name': 'Michał Kowalski', 'worker_communal_cemeteries': 'Tłuszcz', 'worker_location': 'Krosno'},
    {'worker_name': 'Dominik Kowal', 'worker_communal_cemeteries': 'Zamość', 'worker_location': 'Wrocław'}
]

user:list=[]

class User:
    def __init__(self,name, surname,location, post):
        self.name = name
        self.surname = surname
        self.location = location
        self.post = post
        self.coordinates=self.get_coordinates()
        self.marker=map_widget.set_matker(self.coordinates)
