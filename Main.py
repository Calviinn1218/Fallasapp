# main.py
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from datetime import datetime
import json
import os

MAQUINAS_FILE = 'maquinas.json'
FALLAS_FILE = 'fallas.json'


def cargar_maquinas():
    if os.path.exists(MAQUINAS_FILE):
        with open(MAQUINAS_FILE, 'r') as f:
            return json.load(f)
    return []


def guardar_maquinas(maquinas):
    with open(MAQUINAS_FILE, 'w') as f:
        json.dump(maquinas, f)


def cargar_fallas():
    if os.path.exists(FALLAS_FILE):
        with open(FALLAS_FILE, 'r') as f:
            return json.load(f)
    return {}


def guardar_fallas(fallas):
    with open(FALLAS_FILE, 'w') as f:
        json.dump(fallas, f)


class MenuScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Button(text='Registrar Falla', on_press=lambda x: self.manager.current_screen.goto('registro')))
        layout.add_widget(Button(text='Ver Historial', on_press=lambda x: self.manager.current_screen.goto('historial')))
        layout.add_widget(Button(text='Gestionar Máquinas', on_press=lambda x: self.manager.current_screen.goto('maquinas')))
        self.add_widget(layout)

    def goto(self, screen_name):
        self.manager.current = screen_name


class RegistroScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.maquinas = cargar_maquinas()
        self.fallas = cargar_fallas()

        self.spinner = Spinner(text='Selecciona máquina', values=self.maquinas)
        layout.add_widget(self.spinner)

        self.btn_reporte = Button(text='Hora de Reporte')
        self.btn_inicio = Button(text='Inicio de Reparación')
        self.btn_fin = Button(text='Fin de Reparación')
        self.btn_reporte.bind(on_press=self.registrar_reporte)
        self.btn_inicio.bind(on_press=self.registrar_inicio)
        self.btn_fin.bind(on_press=self.registrar_fin)

        layout.add_widget(self.btn_reporte)
        layout.add_widget(self.btn_inicio)
        layout.add_widget(self.btn_fin)

        layout.add_widget(Button(text='Volver', on_press=lambda x: self.manager.current_screen.goto('menu')))
        self.add_widget(layout)

    def registrar_reporte(self, instance):
        self.registrar_evento('reporte')

    def registrar_inicio(self, instance):
        self.registrar_evento('inicio')

    def registrar_fin(self, instance):
        self.registrar_evento('fin')

    def registrar_evento(self, tipo):
        maquina = self.spinner.text
        if maquina == 'Selecciona máquina':
            return

        hoy = datetime.now().strftime('%Y-%m-%d')
        hora = datetime.now().strftime('%H:%M')

        if hoy not in self.fallas:
            self.fallas[hoy] = []

        if tipo == 'reporte':
            self.fallas[hoy].append({'maquina': maquina, 'reporte': hora, 'inicio': '', 'fin': '', 'tiempo_muerto': 0})
        else:
            for falla in reversed(self.fallas[hoy]):
                if falla['maquina'] == maquina and falla[tipo] == '':
                    falla[tipo] = hora
                    if falla['inicio'] and falla['fin']:
                        fmt = '%H:%M'
                        h1 = datetime.strptime(falla['inicio'], fmt)
                        h2 = datetime.strptime(falla['fin'], fmt)
                        falla['tiempo_muerto'] = int((h2 - h1).total_seconds() / 60)
                    break

        guardar_fallas(self.fallas)


class HistorialScreen(Screen):
    def on_enter(self):
        self.mostrar_historial()

    def mostrar_historial(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.input_fecha = TextInput(hint_text='AAAA-MM-DD', size_hint_y=None, height=40, multiline=False)
        self.input_fecha.text = datetime.now().strftime('%Y-%m-%d')
        layout.add_widget(self.input_fecha)

        btn_filtrar = Button(text='Filtrar', size_hint_y=None, height=40)
        btn_filtrar.bind(on_press=lambda x: self.mostrar_historial())
        layout.add_widget(btn_filtrar)

        btn_borrar = Button(text='Eliminar todo ese día', size_hint_y=None, height=40)
        btn_borrar.bind(on_press=self.eliminar_dia)
        layout.add_widget(btn_borrar)

        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        fallas = cargar_fallas()
        fecha = self.input_fecha.text

        total_general = 0
        if fecha in fallas:
            por_maquina = {}
            for f in fallas[fecha]:
                m = f['maquina']
                por_maquina.setdefault(m, []).append(f)

            for maquina, eventos in por_maquina.items():
                grid.add_widget(Label(text=f'[b]{maquina}[/b] ({len(eventos)} fallas)', markup=True))
                eventos.sort(key=lambda x: x['reporte'])
                total_maquina = 0
                for f in eventos:
                    detalle = f"  {f['reporte']} - {f['inicio']} - {f['fin']} ({f['tiempo_muerto']} min)"
                    grid.add_widget(Label(text=detalle))
                    total_maquina += f['tiempo_muerto']
                grid.add_widget(Label(text=f"Total {maquina}: {total_maquina} min\n", bold=True))
                total_general += total_maquina
        else:
            grid.add_widget(Label(text='No hay fallas para esta fecha.'))

        grid.add_widget(Label(text=f'Total general: {total_general} minutos', bold=True))
        scroll.add_widget(grid)
        layout.add_widget(scroll)

        layout.add_widget(Button(text='Volver', on_press=lambda x: self.manager.current_screen.goto('menu')))
        self.add_widget(layout)

    def eliminar_dia(self, instance):
        fecha = self.input_fecha.text
        fallas = cargar_fallas()
        if fecha in fallas:
            del fallas[fecha]
            guardar_fallas(fallas)
            self.mostrar_historial()


class MaquinasScreen(Screen):
    def on_enter(self):
        self.mostrar_maquinas()

    def mostrar_maquinas(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.maquinas = cargar_maquinas()

        for i, m in enumerate(self.maquinas):
            box = BoxLayout(size_hint_y=None, height=40)
            input_renombrar = TextInput(text=m)
            btn_guardar = Button(text='Guardar', size_hint_x=None, width=80)
            btn_guardar.bind(on_press=lambda btn, idx=i, txt=input_renombrar: self.renombrar_maquina(idx, txt.text))
            box.add_widget(input_renombrar)
            box.add_widget(btn_guardar)
            layout.add_widget(box)

        nueva_input = TextInput(hint_text='Nueva máquina')
        btn_agregar = Button(text='Agregar')
        btn_agregar.bind(on_press=lambda x: self.agregar_maquina(nueva_input.text))
        layout.add_widget(nueva_input)
        layout.add_widget(btn_agregar)

        layout.add_widget(Button(text='Volver', on_press=lambda x: self.manager.current_screen.goto('menu')))
        self.add_widget(layout)

    def agregar_maquina(self, nombre):
        if nombre and nombre not in self.maquinas:
            self.maquinas.append(nombre)
            guardar_maquinas(self.maquinas)
            self.mostrar_maquinas()

    def renombrar_maquina(self, idx, nuevo_nombre):
        if nuevo_nombre:
            self.maquinas[idx] = nuevo_nombre
            guardar_maquinas(self.maquinas)
            self.mostrar_maquinas()


class FallasApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(RegistroScreen(name='registro'))
        sm.add_widget(HistorialScreen(name='historial'))
        sm.add_widget(MaquinasScreen(name='maquinas'))
        return sm


if __name__ == '__main__':
    FallasApp().run()
