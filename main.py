"""Contiene la clase Inicio e Interfaz"""
import flet
import requests
from producto import Producto, MenuProducto
from carta import Carta
from pedir import Pago
from menu import Menu
import variables

class Inicio():
    """
    Contiene el método main para iniciar la aplicación
    """
    def main(self:flet.Page) -> None:
        """
        Inicia el programa y la página y lo envía a la interfaz.

        :param page: La página principal que se usará para el programa.
        """
        Interfaz(self)

class Interfaz():
    """
    Tiene los metodos para moverse entre vistas y cargar las bases de la aplicación.
    """

    total = 0.00

    pedir_productos:list[Producto | MenuProducto] = []

    page:flet.Page

    navigation_bar:flet.NavigationBar

    def __init__(self, page: flet.Page) -> None:
        """
        Asigna el evento de cambiar ruta y cambia la ruta actual a '/'.

        :param page: La página a la que se le cambiará la ruta.
        """
        self.page = page
        self.aspecto_base()
        page.on_route_change=lambda _: self.cambiar_ruta()
        self.barra_navegacion()
        page.go("/")

    def aspecto_base(self) -> None:
        """Crea el formato básico para la página."""
        self.page.add(flet.ProgressRing())
        self.page.vertical_alignment=flet.MainAxisAlignment.CENTER
        self.page.horizontal_alignment=flet.CrossAxisAlignment.CENTER
        self.page.adaptive = True
        self.page.title = "Pedir comida"
        self.barra_navegacion()


    def barra_navegacion(self) -> None:
        """Crea y guarda una barra de navegación."""
        navigation_bar = flet.NavigationBar(
            destinations=[
                flet.NavigationDestination(icon=flet.icons.BOOK_OUTLINED,
                    selected_icon=flet.icons.BOOK, label="Carta",),
                flet.NavigationDestination(icon=flet.icons.FOOD_BANK,
                    selected_icon=flet.icons.FOOD_BANK_SHARP, label="Menu del día"),
                flet.NavigationDestination(
                    icon=flet.icons.PRICE_CHECK,
                    label="Pagar",
                ),
            ]
        )
        navigation_bar.on_change=lambda _:self.cambio_navegacion()
        navigation_bar.visible=True
        self.navigation_bar = navigation_bar

    def cambio_navegacion(self) -> None:
        """
        Cambia la interfaz a distintas rutas según la opción seleccionada en la barra de navegación.
        """
        actual = self.navigation_bar.selected_index
        if actual==0:
            self.page.go("/")
        elif actual==1:
            self.page.go("/menu")
        elif actual==2:
            self.page.go("/confirmar")


    def cambiar_ruta(self) -> None:
        """
        Limpia la vista de la página, carga la ruta actual y actualiza la página.

        Si la ruta no está registrada, carga '/'.
        Si no hay productos los intenta cargar. Si no lo consigue solo muestra el aviso.
        """
        self.page.views.clear()
        if not self.pedir_productos:
            productos = self.cargar_productos()
        else:
            productos = True
        if self.page.route == "/confirmar":
            self.navigation_bar.selected_index = 2
            self.calcular_total()
            vista = Pago(self.total, self.page, self.pedir_productos)
            self.page.views.append(vista.cargar_vista(self.total, self.navigation_bar))
        else:
            if productos:
                if self.page.route == "/menu":
                    self.navigation_bar.selected_index = 1
                    vista = Menu(self.pedir_productos)
                    self.page.views.append(vista.cargar_vista(self.page, self.navigation_bar))
                else:
                    self.navigation_bar.selected_index = 0
                    vista = Carta(self.pedir_productos)
                    self.page.views.append(vista.cargar_vista(self.page, self.navigation_bar))
                    vista.cambiar_filtro(self.page)
        self.page.update()

    def cargar_productos(self) -> bool:
        """
        Se conecta al servidor para obtener la se lista de productos
        y guardarlos como objetos productos en una lista. Si no es posible,
        llama a error.

        :returns: True si se carga al menos un producto, False si no.
        """
        try:
            valores_menu = ["Primeros", "Segundos", "Postres", "Bebidas"]
            r = requests.get(variables.PRODUCTOS, timeout=20)
            if r.ok:
                if  r.json() != []:
                    lista = r.json()
                    for p in lista:
                        producto = Producto(nombre = p["name"],
                                            precio = p["price"],
                                            id_producto = p["id"],
                                            descripcion = p["desc"])
                        if p["categ"] in valores_menu:
                            producto.menu=p["categ"]
                        if p["image"] != "\u0000":
                            producto.imagen = p["image"]
                        self.pedir_productos.append(producto)
                    return True
                else:
                    self.error("No hay productos a la venta")
                    return False
            else:
                self.error("No se ha podido conectar con el servidor")
        except Exception as ex:
            self.error("Se ha producido un error")
            print(str(ex))

    def error(self, mensaje:str) -> None:
        """
        Añade un baner con el mensaje recibido y llamam a mostrar_banner().

        :param mensaje: Un texto que se mostrará con el aviso
        """
        self.page.banner = flet.Banner(
            bgcolor=flet.colors.AMBER_100,
            leading=flet.Icon(flet.icons.WARNING_AMBER_ROUNDED, color=flet.colors.AMBER, size=40),
            content=flet.Text(mensaje, color=flet.colors.BLACK),
            actions=[
                flet.TextButton("Reintentar", on_click=lambda _:self.cerrar_banner())]
        )
        self.mostrar_banner()

    def mostrar_banner(self) -> None:
        """
        Muestra el aviso guardado actualmente.
        """
        self.page.banner.open = True
        self.page.update()

    def cerrar_banner(self) -> None:
        """
        Cierra el aviso actual y intenta volver a cargar la ruta actual.
        """
        self.page.banner.open = False
        self.cambiar_ruta()
        self.page.update()

    def calcular_total(self) -> None:
        """
        Multiplica el precio por la cantidad seleccionada de los productos y los suma.
        """
        if len(self.pedir_productos)>0:
            total:float = 0.0
            for producto in self.pedir_productos:
                if isinstance(producto, Producto):
                    total+=producto.precio*float(producto.seleccionado)
            self.total = round(total, 2)

flet.app(target=Inicio.main, assets_dir="assets")
